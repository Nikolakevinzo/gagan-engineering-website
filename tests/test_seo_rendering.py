"""Exercise crawler HTML and discovery routes without contacting production."""
import ast
import copy
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import AsyncMock, patch
import xml.etree.ElementTree as ET

import httpx

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "api"))
with patch.dict(os.environ, {"MONGO_URL": "", "RESEND_API_KEY": ""}):
    from api import index as site
    from api.seed_blogs import SEED_BLOGS


class TestCrawlerRoutes(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.products = copy.deepcopy(site.SEED_PRODUCTS)
        self.blogs = copy.deepcopy(SEED_BLOGS)
        self.product_mock = AsyncMock(return_value=self.products)
        self.blog_mock = AsyncMock(return_value=self.blogs)
        self.detail_mock = AsyncMock(side_effect=lambda slug, published_only=True: next(
            (blog for blog in self.blogs if blog["slug"] == slug), None
        ))
        self.patches = [
            patch.object(site, "get_products_from_db", self.product_mock),
            patch.object(site, "get_blogs_from_db", self.blog_mock),
            patch.object(site, "get_blog_by_slug", self.detail_mock),
        ]
        for mocked in self.patches:
            mocked.start()
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=site.app), base_url="https://test.local")

    async def asyncTearDown(self):
        await self.client.aclose()
        for mocked in reversed(self.patches):
            mocked.stop()

    async def test_latest_gc_article_contains_full_seed_content(self):
        blog = next(b for b in self.blogs if b["slug"] == "gc-roofing-sheet-manufacturing-business-guide")
        response = await self.client.get(f"/_seo/blog/{blog['slug']}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(escape(blog["title"]), response.text)
        self.assertIn(escape(blog["summary"]), response.text)
        self.assertIn(f'content="{escape(blog["targetKeywords"])}"', response.text)
        self.assertEqual(response.text.count("<table>"), sum(s["type"] == "table" for s in blog["content"]))
        for section in blog["content"]:
            self.assertIn(escape(section["heading"]), response.text)
            if section.get("id"):
                self.assertIn(f'id="{section["id"]}"', response.text)
        self.assertIn('href="/products/corrugated-sheets-making-machine"', response.text)
        self.assertIn("IS 277:2018", response.text)
        self.detail_mock.assert_awaited_once_with(blog["slug"], published_only=True)
        self.blog_mock.assert_awaited_with(published_only=True)
        schemas = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', response.text, re.S).group(1))
        self.assertEqual(schemas[0]["datePublished"], "2026-10-02")

    async def test_product_route_retains_specs_without_stock_or_offer_claims(self):
        product = self.products[0]
        response = await self.client.get(f"/_seo/products/{product['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(escape(product["name"]), response.text)
        for key, value in product["specs"].items():
            self.assertIn(escape(str(key)), response.text)
            self.assertIn(escape(str(value)), response.text)
        self.assertNotIn('property="product:availability"', response.text)
        schemas = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', response.text, re.S).group(1))
        product_schema = next(schema for schema in schemas if schema["@type"] == "Product")
        self.assertNotIn("offers", product_schema)
        self.assertNotIn("aggregateRating", product_schema)

    async def test_blog_storage_failure_propagates_503_without_seed_fallback(self):
        self.blog_mock.side_effect = site.HTTPException(status_code=503, detail="Blog storage unavailable")
        for path in ("/_seo/blog", "/_seo/blog/gc-roofing-sheet-manufacturing-business-guide", "/sitemap.xml"):
            with self.subTest(path=path):
                response = await self.client.get(path)
                self.assertEqual(response.status_code, 503)
                self.assertNotIn("GC Roofing", response.text)

    async def test_listing_and_footer_use_current_published_articles(self):
        self.blogs[:] = [{"slug": "new-database-article", "title": "New database article", "summary": "Actual database summary"}]
        response = await self.client.get("/_seo/blog")
        main = response.text.split("<main>")[1].split("</main>")[0]
        self.assertIn('href="/blog/new-database-article"', main)
        self.assertIn("Actual database summary", main)
        self.assertNotIn('href="/blog/gc-roofing-sheet-manufacturing-business-guide"', response.text)

    async def test_content_and_json_ld_escape_untrusted_article_data(self):
        payload = '</script><script>alert("injected")</script>'
        self.blogs[:] = [{
            "slug": "safe", "title": payload, "summary": payload,
            "content": [
                {"type": "section", "id": '\" onclick=\"bad', "heading": payload,
                 "text": f"{payload} **bold** [machine](/products/test) [unsafe](javascript:alert) [malformed](https://[)",
                 "items": [payload, "**safe item**"]},
                {"type": "table", "heading": "Table", "headers": [payload], "rows": [[payload, 0]]},
            ],
            "faqs": [{"q": payload, "a": payload}],
        }]
        response = await self.client.get("/_seo/blog/safe")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(payload, response.text)
        self.assertIn(escape(payload), response.text)
        self.assertIn("<strong>bold</strong>", response.text)
        self.assertIn('href="/products/test"', response.text)
        self.assertNotIn('href="javascript:', response.text)
        self.assertNotIn('href="https://[', response.text)
        self.assertIn("[malformed](https://[)", response.text)
        self.assertIn("<td>0</td>", response.text)
        schemas = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', response.text, re.S).group(1))
        self.assertEqual(schemas[0]["headline"], payload)

    async def test_unknown_public_paths_are_noindex_404(self):
        for path in ("products/missing", "blog/missing", "products/category/missing", "missing-page"):
            with self.subTest(path=path):
                response = await self.client.get(f"/_seo/{path}")
                self.assertEqual(response.status_code, 404)
                self.assertIn('content="noindex, follow"', response.text)
                self.assertEqual(response.headers["x-robots-tag"], "noindex, follow")
                self.assertNotIn('<link rel="canonical"', response.text)

    async def test_head_and_vercel_rewrite_match_get_without_body(self):
        for path in ("blog/gc-roofing-sheet-manufacturing-business-guide", "blog/missing"):
            with self.subTest(path=path):
                get = await self.client.get("/api/index.py", params={"__seo_path": path})
                head = await self.client.head("/api/index.py", params={"__seo_path": path})
                self.assertEqual(head.status_code, get.status_code)
                self.assertEqual(head.content, b"")
                self.assertEqual(head.headers["content-length"], get.headers["content-length"])
                self.assertEqual(head.headers["x-prerender"], "1")

    async def test_category_body_and_itemlist_have_matching_products(self):
        self.products[:] = [
            {"id": "facing", "name": "Facing machine", "category": "Facing Machines"},
            {"id": "bra", "name": "Bra machine", "categorySlug": "bra-cup-moulding-machine"},
            {"id": "decoiler", "name": "Decoiler", "category": "Hydraulic Decoiler"},
        ]
        expected_by_category = {
            "roll-forming-sheet-metal": ["decoiler"],
            "cut-to-length-line": [],
            "bra-cup-moulding-machine": ["bra"],
            "bending-machines": [],
            "facing-machines": ["facing"],
            "threading-machines": [],
            "recoiling-decoiling-machines": ["decoiler"],
        }
        self.assertEqual(set(site.CATEGORY_SEO), set(expected_by_category))
        for slug, expected_ids in expected_by_category.items():
            with self.subTest(category=slug):
                response = await self.client.get(f"/_seo/products/category/{slug}")
                self.assertEqual(response.status_code, 200)
                main = response.text.split("<main>")[1].split("</main>")[0]
                expected = [p for p in self.products if p["id"] in expected_ids]
                for product in self.products:
                    self.assertEqual(f'href="/products/{product["id"]}"' in main, product in expected)
                schemas = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', response.text, re.S).group(1))
                listing = next(s for s in schemas if s["@type"] == "ItemList")
                self.assertEqual([s["name"] for s in listing["itemListElement"]], [p["name"] for p in expected])
        self.assertEqual(len(site.CATEGORY_SEO), 7)

    async def test_sitemap_uses_authoritative_articles_and_real_dates(self):
        self.blogs[:] = [{"slug": "published&article", "title": "Published", "date": "2026-10-02", "updatedAt": "2026-10-04T15:30:00Z"}]
        self.products[:] = [
            {"id": "recorded", "name": "Name & <tool>", "image": "https://example.org/image?a=1&b=2", "updatedAt": datetime(2026, 9, 30, tzinfo=timezone.utc)},
            {"id": "unknown-date", "name": "No date", "updatedAt": "invalid"},
        ]
        response = await self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "i": "http://www.google.com/schemas/sitemap-image/1.1"}
        root = ET.fromstring(response.content)
        entries = {node.find("s:loc", namespace).text: node for node in root.findall("s:url", namespace)}
        blog = entries[f"{site.WEBSITE_URL}/blog/published%26article"]
        self.assertEqual(blog.find("s:lastmod", namespace).text, "2026-10-04")
        product = entries[f"{site.WEBSITE_URL}/products/recorded"]
        self.assertEqual(product.find("s:lastmod", namespace).text, "2026-09-30")
        self.assertEqual(product.find("i:image/i:loc", namespace).text, "https://example.org/image?a=1&b=2")
        self.assertEqual(product.find("i:image/i:title", namespace).text, "Name & <tool>")
        self.assertIsNone(entries[f"{site.WEBSITE_URL}/products/unknown-date"].find("s:lastmod", namespace))
        self.assertIsNone(entries[f"{site.WEBSITE_URL}/"].find("s:lastmod", namespace))
        self.assertFalse(any("gc-roofing-sheet" in url for url in entries))
        self.blog_mock.assert_awaited_once_with(published_only=True)


def _load_discovery_functions(path):
    """Run only public discovery definitions, without backend startup or secrets."""
    tree = ast.parse(path.read_text())
    namespace = {"Response": site.Response, "datetime": datetime, "WEBSITE_URL": site.WEBSITE_URL}
    definitions = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("PAGE_META", "CATEGORY_SEO"):
                    namespace[target.id] = ast.literal_eval(node.value)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in (
            "_content_lastmod", "_absolute_image_url", "sitemap", "google_merchant_feed"
        ):
            node.decorator_list = []
            definitions.append(node)
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


class TestDiscoveryBackendParity(unittest.IsolatedAsyncioTestCase):
    async def test_both_sitemaps_use_published_records_and_real_dates(self):
        outputs = []
        for filename in ("api/index.py", "backend/server.py"):
            with self.subTest(backend=filename):
                backend = _load_discovery_functions(ROOT_DIR / filename)
                backend["get_products_from_db"] = AsyncMock(return_value=[
                    {"id": "tool&one", "name": "Tool & <one>", "image": "/machine.png?width=1&height=2", "updatedAt": "2026-10-03T09:30:00Z"},
                    {"id": "unknown-date", "name": "No recorded date"},
                ])
                backend["get_blogs_from_db"] = AsyncMock(return_value=[
                    {"slug": "published-article", "date": "2026-10-02"},
                ])
                response = await backend["sitemap"]()
                namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "i": "http://www.google.com/schemas/sitemap-image/1.1"}
                root = ET.fromstring(response.body)
                entries = {node.find("s:loc", namespace).text: node for node in root.findall("s:url", namespace)}
                self.assertEqual(entries[f"{site.WEBSITE_URL}/blog/published-article"].find("s:lastmod", namespace).text, "2026-10-02")
                product = entries[f"{site.WEBSITE_URL}/products/tool%26one"]
                self.assertEqual(product.find("s:lastmod", namespace).text, "2026-10-03")
                self.assertEqual(product.find("i:image/i:loc", namespace).text, f"{site.WEBSITE_URL}/machine.png?width=1&height=2")
                self.assertEqual(product.find("i:image/i:title", namespace).text, "Tool & <one>")
                self.assertIsNone(entries[f"{site.WEBSITE_URL}/"].find("s:lastmod", namespace))
                self.assertIsNone(entries[f"{site.WEBSITE_URL}/products/unknown-date"].find("s:lastmod", namespace))
                backend["get_blogs_from_db"].assert_awaited_once_with(published_only=True)
                outputs.append(response.body)
        self.assertEqual(outputs[0], outputs[1])

    async def test_both_feeds_are_empty_and_need_no_database(self):
        outputs = []
        for filename in ("api/index.py", "backend/server.py"):
            with self.subTest(backend=filename):
                backend = _load_discovery_functions(ROOT_DIR / filename)
                backend["get_products_from_db"] = AsyncMock(side_effect=AssertionError("Feed must not invent offers from catalogue records"))
                response = await backend["google_merchant_feed"]()
                channel = ET.fromstring(response.body).find("channel")
                self.assertIsNotNone(channel)
                self.assertEqual(channel.findall("item"), [])
                backend["get_products_from_db"].assert_not_awaited()
                outputs.append(response.body)
        self.assertEqual(outputs[0], outputs[1])

    async def test_both_sitemaps_preserve_storage_failures(self):
        for filename in ("api/index.py", "backend/server.py"):
            with self.subTest(backend=filename):
                backend = _load_discovery_functions(ROOT_DIR / filename)
                backend["get_products_from_db"] = AsyncMock(return_value=[])
                backend["get_blogs_from_db"] = AsyncMock(side_effect=site.HTTPException(status_code=503, detail="Unavailable"))
                with self.assertRaises(site.HTTPException) as raised:
                    await backend["sitemap"]()
                self.assertEqual(raised.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
