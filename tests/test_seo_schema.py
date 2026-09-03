"""
Automated Test Suite for Google Search Console & Rich Results Compliance
Validates Product Schema JSON-LD, Merchant Feed XML, and SEO Meta standards.
"""
import unittest
import json
import xml.etree.ElementTree as ET
import sys
from pathlib import Path

# Add project root and api to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "api"))

from api.index import (
    _build_product_schema,
    get_product_sku,
    PRODUCT_SKUS,
    SEED_PRODUCTS,
    WEBSITE_URL,
)

class TestGoogleSearchConsoleProductSchema(unittest.TestCase):
    """Verify that all 10 products generate 100% compliant Google Rich Results Schema."""

    def test_all_products_satisfy_gsc_requirements(self):
        for product in SEED_PRODUCTS:
            p_id = product["id"]
            canonical = f"{WEBSITE_URL}/products/{p_id}"
            schema_json = _build_product_schema(product, canonical)
            schemas = json.loads(schema_json)
            
            # Find the Product schema
            prod_schema = next((s for s in schemas if s.get("@type") == "Product"), None)
            self.assertIsNotNone(prod_schema, f"Missing Product schema for {p_id}")

            # 1. SKU length validation (Must be <= 50 characters, fixes GSC 'Invalid string length in field sku')
            sku = prod_schema.get("sku")
            self.assertIsNotNone(sku, f"Missing sku for {p_id}")
            self.assertTrue(len(sku) <= 50, f"SKU too long ({len(sku)} chars): '{sku}' for {p_id}")
            self.assertTrue(len(sku) >= 5, f"SKU too short: '{sku}' for {p_id}")

            # 2. MPN validation
            mpn = prod_schema.get("mpn")
            self.assertIsNotNone(mpn, f"Missing mpn for {p_id}")
            self.assertTrue(len(mpn) <= 50)

            # 3. Image validation (Must be absolute URL)
            images = prod_schema.get("image", [])
            self.assertTrue(len(images) > 0, f"Missing images for {p_id}")
            for img in images:
                self.assertTrue(img.startswith("http://") or img.startswith("https://"), f"Image URL must be absolute: {img}")

            # 4. Offers validation
            offers = prod_schema.get("offers")
            self.assertIsNotNone(offers, f"Missing offers for {p_id}")
            self.assertEqual(offers.get("priceCurrency"), "INR")
            self.assertIn("priceValidUntil", offers)

            # 5. hasMerchantReturnPolicy validation (Fixes GSC 'Missing field hasMerchantReturnPolicy')
            return_policy = offers.get("hasMerchantReturnPolicy")
            self.assertIsNotNone(return_policy, f"Missing hasMerchantReturnPolicy for {p_id}")
            self.assertEqual(return_policy.get("@type"), "MerchantReturnPolicy")
            self.assertEqual(return_policy.get("applicableCountry"), "IN")
            self.assertTrue(return_policy.get("merchantReturnDays", 0) > 0)
            self.assertTrue(return_policy.get("url", "").startswith("https://"))

            # 6. shippingDetails & addressCountry validation (Fixes GSC 'Missing field addressCountry')
            shipping = offers.get("shippingDetails")
            self.assertIsNotNone(shipping, f"Missing shippingDetails for {p_id}")
            destinations = shipping.get("shippingDestination", [])
            self.assertTrue(len(destinations) > 0, f"Missing destinations for {p_id}")
            for dest in destinations:
                self.assertEqual(dest.get("@type"), "DefinedRegion")
                country = dest.get("addressCountry")
                self.assertIsNotNone(country, f"Every DefinedRegion must have addressCountry for {p_id}")
                self.assertEqual(len(country), 2, f"addressCountry must be 2-letter ISO code: {country}")

            # 7. transitTime validation (Fixes GSC 'Missing field transitTime')
            delivery = shipping.get("deliveryTime")
            self.assertIsNotNone(delivery, f"Missing deliveryTime for {p_id}")
            self.assertIn("handlingTime", delivery, f"Missing handlingTime for {p_id}")
            self.assertIn("transitTime", delivery, f"Missing transitTime for {p_id}")
            self.assertTrue(delivery["transitTime"].get("minValue", 0) > 0)
            self.assertTrue(delivery["transitTime"].get("maxValue", 0) > 0)

            # 8. aggregateRating validation (Fixes GSC 'Missing field aggregateRating')
            rating = prod_schema.get("aggregateRating")
            self.assertIsNotNone(rating, f"Missing aggregateRating for {p_id}")
            self.assertEqual(rating.get("@type"), "AggregateRating")
            self.assertTrue(float(rating.get("ratingValue", 0)) >= 4.0)
            self.assertTrue(int(rating.get("reviewCount", 0)) > 0)

            # 9. review validation (Fixes GSC 'Missing field review')
            reviews = prod_schema.get("review", [])
            self.assertTrue(len(reviews) > 0, f"Missing review list for {p_id}")
            for rev in reviews:
                self.assertEqual(rev.get("@type"), "Review")
                self.assertIn("author", rev)
                self.assertIn("reviewRating", rev)
                self.assertIn("reviewBody", rev)
                self.assertIn("datePublished", rev)


class TestGoogleMerchantFeedXML(unittest.TestCase):
    """Verify static and generated Google Merchant feeds pass character constraints."""

    def test_static_merchant_feed_skus(self):
        feed_path = ROOT_DIR / "frontend" / "public" / "google-merchant-feed.xml"
        self.assertTrue(feed_path.exists())
        
        tree = ET.parse(str(feed_path))
        root = tree.getroot()
        channel = root.find("channel")
        items = channel.findall("item")
        self.assertEqual(len(items), 10, "Static feed should contain all 10 products")

        namespaces = {'g': 'http://base.google.com/ns/1.0'}
        for item in items:
            g_id = item.find("g:id", namespaces)
            self.assertIsNotNone(g_id)
            self.assertTrue(len(g_id.text) <= 50, f"g:id too long ({len(g_id.text)}): {g_id.text}")

            img = item.find("g:image_link", namespaces)
            self.assertIsNotNone(img)
            self.assertTrue(img.text.startswith("https://"), f"image_link must be https: {img.text}")


if __name__ == "__main__":
    unittest.main()
