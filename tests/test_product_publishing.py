"""Product publishing uses the same isolated, network-free backend harness as blogs."""
import copy
import unittest

from fastapi import HTTPException

from tests.test_blog_publishing import ROOT, Collection, load_backend


PRODUCTS = [
    {"id": "seed-product", "name": "Seed product", "category": "Machinery", "categorySlug": "machinery", "specs": {"Fixture": "Unchanged"}},
    {"id": "other-seed", "name": "Other seed", "category": "Machinery", "categorySlug": "machinery"},
]


class ProductPublishingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.backends = [(path, load_backend(ROOT / path)) for path in ("api/index.py", "backend/server.py")]
        for _, backend in self.backends:
            backend["_mem_products"] = copy.deepcopy(PRODUCTS)
            backend["SEED_PRODUCTS"] = copy.deepcopy(PRODUCTS)
            backend["db"]["products"] = Collection()

    def new_product(self, backend, product_id="new-product"):
        return backend["ProductCreate"](id=product_id, name="New product", category="Machinery", categorySlug="machinery")

    async def test_db_content_and_deletion_markers_override_seed(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["db"]["products"].docs = [{**PRODUCTS[0], "name": "DB version"}]
                listed = await backend["get_products_from_db"]()
                self.assertEqual(len(listed), 2)
                self.assertEqual(listed[0]["name"], "DB version")
                backend["db"]["products"].docs[0]["deleted"] = True
                self.assertIsNone(await backend["get_product_by_id"]("seed-product"))
                self.assertEqual([p["id"] for p in await backend["get_products_from_db"]()], ["other-seed"])

    async def test_delete_seed_survives_startup_and_restore_reuses_marker(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                await backend["admin_delete_product"]("seed-product", username="test")
                await backend["seed_database"]()
                await backend["seed_database"]()
                self.assertIsNone(await backend["get_product_by_id"]("seed-product"))
                self.assertEqual([p["id"] for p in await backend["get_products_from_db"]()], ["other-seed"])
                result = await backend["admin_create_product"](self.new_product(backend, "seed-product"), username="test")
                self.assertEqual(result["status"], "created")
                self.assertNotIn("_id", result["product"])
                self.assertEqual(len([p for p in backend["db"]["products"].docs if p["id"] == "seed-product"]), 1)
                self.assertIsNotNone(await backend["get_product_by_id"]("seed-product"))

    async def test_editing_fallback_product_persists_complete_record(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                saved = await backend["admin_update_product"]("seed-product", backend["ProductUpdate"](name="Saved edit"), username="test")
                self.assertEqual(saved["product"]["name"], "Saved edit")
                self.assertEqual(backend["db"]["products"].docs[0]["specs"], PRODUCTS[0]["specs"])
                self.assertEqual(backend["_mem_products"], PRODUCTS)

    async def test_create_conflicts_do_not_duplicate_product(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                payload = self.new_product(backend)
                await backend["admin_create_product"](payload, username="test")
                with self.assertRaises(HTTPException) as caught:
                    await backend["admin_create_product"](payload, username="test")
                self.assertEqual(caught.exception.status_code, 409)
                self.assertEqual(len(backend["db"]["products"].docs), 1)
                self.assertEqual(backend["_mem_products"], PRODUCTS)

    async def test_no_db_is_read_only_and_failed_writes_never_mutate_memory(self):
        for path, backend in self.backends:
            for configured in (False, True):
                with self.subTest(backend=path, configured=configured):
                    backend["db"] = {"products": Collection()} if configured else None
                    if configured:
                        backend["db"]["products"].fail_writes = True
                    self.assertEqual(await backend["get_products_from_db"](), PRODUCTS)
                    self.assertEqual(await backend["get_product_by_id"]("seed-product"), PRODUCTS[0])
                    for name, args in [
                        ("admin_create_product", (self.new_product(backend),)),
                        ("admin_update_product", ("seed-product", backend["ProductUpdate"](name="Edit"))),
                        ("admin_delete_product", ("seed-product",)),
                        ("admin_import_products", ([self.new_product(backend)],)),
                    ]:
                        with self.assertRaises(HTTPException) as caught:
                            await backend[name](*args, username="test")
                        self.assertEqual(caught.exception.status_code, 503)
                    self.assertEqual(backend["_mem_products"], PRODUCTS)
                    if configured:
                        self.assertEqual(backend["db"]["products"].docs, [])

    async def test_db_read_failure_does_not_resurrect_deleted_seed(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["db"]["products"].fail_reads = True
                for name, args in [("get_products_from_db", ()), ("get_product_by_id", ("seed-product",))]:
                    with self.assertRaises(HTTPException) as caught:
                        await backend[name](*args)
                    self.assertEqual(caught.exception.status_code, 503)

    async def test_bulk_import_skips_duplicates_and_reports_partial_failure(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                payload = self.new_product(backend)
                result = await backend["admin_import_products"]([payload, payload], username="test")
                self.assertEqual(result["created_ids"], ["new-product"])
                self.assertEqual(result["skipped_ids"], ["new-product"])
                collection = Collection()
                backend["db"]["products"] = collection
                replace_one = collection.replace_one

                async def fail_second(query, replacement, upsert=False):
                    if collection.docs:
                        raise RuntimeError("Storage unavailable")
                    await replace_one(query, replacement, upsert=upsert)

                collection.replace_one = fail_second
                with self.assertRaises(HTTPException) as caught:
                    await backend["admin_import_products"]([self.new_product(backend, "first"), self.new_product(backend, "second")], username="test")
                self.assertEqual(caught.exception.status_code, 503)
                self.assertEqual(caught.exception.detail["created_ids"], ["first"])
                self.assertEqual([p["id"] for p in collection.docs], ["first"])
                self.assertEqual(backend["_mem_products"], PRODUCTS)


if __name__ == "__main__":
    unittest.main()
