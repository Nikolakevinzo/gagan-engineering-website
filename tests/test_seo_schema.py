"""Check truthful catalogue markup, without claiming rich-result eligibility."""
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "api"))
with patch.dict(os.environ, {"MONGO_URL": "", "RESEND_API_KEY": ""}):
    from api import index as site


class TestProductSchema(unittest.TestCase):
    def test_catalogue_identity_without_invented_commerce(self):
        for product in site.SEED_PRODUCTS:
            with self.subTest(product=product["id"]):
                schemas = json.loads(site._build_product_schema(
                    product, f"{site.WEBSITE_URL}/products/{product['id']}"
                ))
                schema = next(s for s in schemas if s["@type"] == "Product")
                self.assertEqual(schema["name"], product["name"])
                self.assertTrue(5 <= len(schema["sku"]) <= 50)
                self.assertEqual(schema["mpn"], schema["sku"])
                self.assertTrue(all(image.startswith(("https://", "http://")) for image in schema["image"]))
                for unsupported in ("offers", "review", "aggregateRating"):
                    self.assertNotIn(unsupported, schema)

    def test_relative_image_and_json_ld_script_safety(self):
        product = {"id": "test", "name": "</script><script>alert(1)</script>", "image": "/machine.png"}
        rendered = site._build_product_schema(product, f"{site.WEBSITE_URL}/products/test")
        self.assertNotIn("</script>", rendered)
        schema = json.loads(rendered)[0]
        self.assertEqual(schema["name"], product["name"])
        self.assertEqual(schema["image"], [f"{site.WEBSITE_URL}/machine.png"])


class TestMerchantFeed(unittest.IsolatedAsyncioTestCase):
    async def test_dynamic_feed_has_no_estimated_offers(self):
        response = await site.google_merchant_feed()
        channel = ET.fromstring(response.body).find("channel")
        self.assertIsNotNone(channel)
        self.assertEqual(channel.findall("item"), [])

    def test_static_feed_has_no_estimated_offers(self):
        channel = ET.parse(ROOT_DIR / "frontend/public/google-merchant-feed.xml").getroot().find("channel")
        self.assertIsNotNone(channel)
        self.assertEqual(channel.findall("item"), [])


if __name__ == "__main__":
    unittest.main()
