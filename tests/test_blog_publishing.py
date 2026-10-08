"""Exercise both blog backends without importing startup, credentials or network clients."""
import ast
import copy
import logging
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import HTTPException
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[1]
SEEDS = [
    {"slug": "seed", "title": "Seed", "summary": "Seed summary", "published": True, "date": "2026-10-02", "content": [{"type": "section", "heading": "Details", "text": "Full article"}]},
    {"slug": "missing-seed", "title": "Missing seed", "summary": "Summary", "published": True, "date": "2026-09-20"},
]


class Cursor:
    def __init__(self, docs):
        self.docs = docs

    async def to_list(self, length=None):
        return copy.deepcopy(self.docs if length is None else self.docs[:length])


class Collection:
    def __init__(self, docs=()):
        self.docs = copy.deepcopy(list(docs))
        self.fail_reads = False
        self.fail_writes = False

    def matching(self, query):
        return [d for d in self.docs if all(d.get(k) == v for k, v in query.items())]

    def find(self, query, projection=None):
        if self.fail_reads:
            raise RuntimeError("Storage unavailable")
        return Cursor(self.matching(query))

    async def find_one(self, query, projection=None):
        if self.fail_reads:
            raise RuntimeError("Storage unavailable")
        return next(iter(copy.deepcopy(self.matching(query))), None)

    async def count_documents(self, query):
        return len(self.matching(query))

    async def insert_one(self, document):
        if self.fail_writes:
            raise RuntimeError("Storage unavailable")
        self.docs.append(copy.deepcopy(document))

    async def update_one(self, query, update, upsert=False):
        if self.fail_writes:
            raise RuntimeError("Storage unavailable")
        if "_id" in update.get("$unset", {}):
            raise RuntimeError("Cannot update immutable _id")
        matches = self.matching(query)
        if matches:
            doc = matches[0]
        elif upsert:
            doc = {**query, **copy.deepcopy(update.get("$setOnInsert", {}))}
            self.docs.append(doc)
        else:
            return
        doc.update(copy.deepcopy(update.get("$set", {})))
        for key in update.get("$unset", {}):
            doc.pop(key, None)

    async def replace_one(self, query, replacement, upsert=False):
        if self.fail_writes:
            raise RuntimeError("Storage unavailable")
        matches = self.matching(query)
        if matches:
            self.docs[self.docs.index(matches[0])] = copy.deepcopy(replacement)
        elif upsert:
            self.docs.append(copy.deepcopy(replacement))


def load_backend(path):
    """Compile only the tested definitions; never execute module-level app setup."""
    names = {
        "BlogContentItem", "BlogTOCItem", "BlogArticleCreate", "BlogArticleUpdate",
        "get_blogs_from_db", "get_blog_by_slug", "seed_database",
        "admin_create_blog", "admin_update_blog", "admin_delete_blog",
        "FAQItem", "ProductCreate", "ProductUpdate", "_validate_youtube_url",
        "get_products_from_db", "get_product_by_id", "admin_create_product",
        "admin_update_product", "admin_delete_product", "admin_import_products",
    }
    definitions = []
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            node.decorator_list = []
            definitions.append(node)
    namespace = {
        "BaseModel": BaseModel, "List": List, "Dict": Dict, "Optional": Optional,
        "datetime": datetime, "timezone": timezone, "HTTPException": HTTPException,
        "Depends": lambda _fn: None, "verify_admin": None,
        "logger": logging.getLogger("blog-publishing-test"),
        "SEED_BLOGS": copy.deepcopy(SEEDS), "SEED_PRODUCTS": [],
        "_mem_blogs": copy.deepcopy(SEEDS),
        "_mem_products": [],
        "db": {"blogs": Collection(), "products": Collection([{"id": "existing"}])},
    }
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


class BlogPublishingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.backends = [(path, load_backend(ROOT / path)) for path in ("api/index.py", "backend/server.py")]

    async def test_db_draft_suppresses_seed_in_list_and_detail(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                draft = {**SEEDS[0], "published": False, "title": "Edited draft"}
                backend["db"]["blogs"].docs = [draft]
                public = await backend["get_blogs_from_db"]()
                self.assertEqual([b["slug"] for b in public], ["missing-seed"])
                self.assertIsNone(await backend["get_blog_by_slug"]("seed", published_only=True))
                self.assertEqual((await backend["get_blog_by_slug"]("seed"))["title"], "Edited draft")
                self.assertEqual(len(await backend["get_blogs_from_db"](published_only=False)), 2)

    async def test_db_content_wins_and_missing_seeds_merge_once(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                article = {**SEEDS[0], "title": "Current DB version"}
                backend["db"]["blogs"].docs = [article]
                listed = await backend["get_blogs_from_db"]()
                self.assertEqual([b["slug"] for b in listed], ["seed", "missing-seed"])
                self.assertEqual(listed[0]["title"], "Current DB version")
                self.assertEqual(listed[0]["content"], article["content"])
                self.assertEqual(await backend["get_blog_by_slug"]("seed", published_only=True), listed[0])

    async def test_delete_seed_stays_deleted_after_restart_seeding(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                self.assertEqual((await backend["admin_delete_blog"]("seed", username="test"))["status"], "deleted")
                await backend["seed_database"]()
                await backend["seed_database"]()
                docs = backend["db"]["blogs"].docs
                self.assertEqual(len([b for b in docs if b["slug"] == "seed"]), 1)
                self.assertTrue(next(b for b in docs if b["slug"] == "seed")["deleted"])
                self.assertIsNone(await backend["get_blog_by_slug"]("seed"))
                self.assertEqual([b["slug"] for b in await backend["get_blogs_from_db"](False)], ["missing-seed"])

    async def test_editing_missing_seed_persists_full_article_and_unpublish(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                result = await backend["admin_update_blog"]("seed", backend["BlogArticleUpdate"](published=False, title="Saved draft"), username="test")
                self.assertEqual(result["article"]["title"], "Saved draft")
                persisted = backend["db"]["blogs"].docs[0]
                self.assertEqual(persisted["content"], SEEDS[0]["content"])
                self.assertFalse(persisted["published"])
                self.assertEqual(backend["_mem_blogs"], SEEDS)
                await backend["seed_database"]()
                self.assertIsNone(await backend["get_blog_by_slug"]("seed", published_only=True))

    async def test_create_and_recreate_deleted_slug_without_duplicates(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                create = backend["BlogArticleCreate"](slug="new-post", title="New article", summary="Summary")
                created = await backend["admin_create_blog"](create, username="test")
                self.assertEqual(created["status"], "created")
                self.assertNotIn("_id", created["article"])
                with self.assertRaises(HTTPException) as caught:
                    await backend["admin_create_blog"](create, username="test")
                self.assertEqual(caught.exception.status_code, 409)
                await backend["admin_delete_blog"]("new-post", username="test")
                await backend["admin_create_blog"](create, username="test")
                self.assertEqual(len(backend["db"]["blogs"].docs), 1)
                self.assertIsNotNone(await backend["get_blog_by_slug"]("new-post", published_only=True))
                self.assertEqual(backend["_mem_blogs"], SEEDS)

    async def test_failed_writes_return_503_without_memory_only_success(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["db"]["blogs"].fail_writes = True
                operations = [
                    ("admin_create_blog", (backend["BlogArticleCreate"](slug="new", title="New", summary="Summary"),)),
                    ("admin_update_blog", ("seed", backend["BlogArticleUpdate"](published=False))),
                    ("admin_delete_blog", ("seed",)),
                ]
                for name, args in operations:
                    with self.assertRaises(HTTPException) as caught:
                        await backend[name](*args, username="test")
                    self.assertEqual(caught.exception.status_code, 503)
                self.assertEqual(backend["_mem_blogs"], SEEDS)
                self.assertEqual(backend["db"]["blogs"].docs, [])

    async def test_no_db_allows_public_reads_but_rejects_admin_writes(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["db"] = None
                self.assertEqual(len(await backend["get_blogs_from_db"]()), len(SEEDS))
                self.assertEqual((await backend["get_blog_by_slug"]("seed", True))["content"], SEEDS[0]["content"])
                for name, args in [
                    ("admin_create_blog", (backend["BlogArticleCreate"](title="New", summary="Summary"),)),
                    ("admin_update_blog", ("seed", backend["BlogArticleUpdate"](title="Edited"))),
                    ("admin_delete_blog", ("seed",)),
                ]:
                    with self.assertRaises(HTTPException) as caught:
                        await backend[name](*args, username="test")
                    self.assertEqual(caught.exception.status_code, 503)
                self.assertEqual(backend["_mem_blogs"], SEEDS)

    async def test_configured_db_read_failure_does_not_resurrect_seed(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["db"]["blogs"].fail_reads = True
                for name, args in [("get_blogs_from_db", ()), ("get_blog_by_slug", ("seed", True))]:
                    with self.assertRaises(HTTPException) as caught:
                        await backend[name](*args)
                    self.assertEqual(caught.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
