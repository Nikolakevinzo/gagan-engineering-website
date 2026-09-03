"""
Gagan Engineering Works — System Test Suite
Tests API routing, security access control, honeypot detection, and cloud database integrity.
"""
import unittest
import os
import sys
from pathlib import Path

# Add project root and api to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "api"))

from api.index import (
    app,
    verify_admin,
    ContactLeadCreate,
    ProductCreate,
    ProductUpdate,
    SEED_PRODUCTS,
    _validate_youtube_url,
)
from fastapi import HTTPException

class DummyRequest:
    """Mock Request for unit testing auth dependencies."""
    def __init__(self, headers=None, client_host="127.0.0.1"):
        self.headers = headers or {}
        class Client:
            host = client_host
        self.client = Client()

class TestSystemSecurity(unittest.TestCase):
    """Test security measures, credentials, and honeypot trapping."""

    def test_verify_admin_valid_env_credentials(self):
        """Valid admin credentials must be accepted."""
        req = DummyRequest(headers={
            "X-Admin-User": "admin",
            "X-Admin-Pass": "gaganworks2006",
        })
        user = verify_admin(req)
        self.assertEqual(user, "admin")

    def test_verify_admin_rejects_purged_backdoor(self):
        """Purged backdoor string 'Enrique7@' must be rejected with 401."""
        req = DummyRequest(headers={
            "X-Admin-User": "admin",
            "X-Admin-Pass": "Enrique7@",
        })
        with self.assertRaises(HTTPException) as ctx:
            verify_admin(req)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_verify_admin_rejects_missing_credentials(self):
        """Missing credentials must be rejected with 401."""
        req = DummyRequest(headers={})
        with self.assertRaises(HTTPException) as ctx:
            verify_admin(req)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_honeypot_field_present_in_model(self):
        """ContactLeadCreate must accept website_hp honeypot field."""
        payload = ContactLeadCreate(
            name="Test User",
            email="test@example.com",
            phone="+91 98765 43210",
            message="Test inquiry",
            website_hp="http://spam-bot.com"
        )
        self.assertEqual(payload.website_hp, "http://spam-bot.com")

    def test_youtube_url_validator(self):
        """Only genuine YouTube URLs should be accepted."""
        valid_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(_validate_youtube_url(valid_url), valid_url)

        valid_short = "https://youtu.be/dQw4w9WgXcQ"
        self.assertEqual(_validate_youtube_url(valid_short), valid_short)

        with self.assertRaises(HTTPException):
            _validate_youtube_url("https://vimeo.com/12345678")


class TestCatalogDataIntegrity(unittest.TestCase):
    """Test product catalog definitions and specifications."""

    def test_seed_products_count(self):
        """Catalog must contain all 10 core industrial machines."""
        self.assertEqual(len(SEED_PRODUCTS), 10)

    def test_ctl_machine_image_asset(self):
        """Automatic CTL machine must use dedicated authentic asset."""
        ctl = next((p for p in SEED_PRODUCTS if p["id"] == "automatic-ctl-machine"), None)
        self.assertIsNotNone(ctl)
        self.assertEqual(ctl["image"], "/automatic-ctl.png")

    def test_pipe_counter_boring_image(self):
        """Semi-Automatic Pipe Counter Boring machine must have valid image."""
        pipe_machine = next((p for p in SEED_PRODUCTS if p["id"] == "semi-automatic-pipe-counter-boring-and-facing-machine"), None)
        self.assertIsNotNone(pipe_machine)
        self.assertTrue(pipe_machine["image"].startswith("https://5.imimg.com/"))


class TestBlogSystemIntegrity(unittest.TestCase):
    """Test blog catalog, seeding, models, and image assets."""

    def test_seed_blogs_count(self):
        """Must have at least 8 core industrial pillar articles."""
        from api.seed_blogs import SEED_BLOGS
        self.assertGreaterEqual(len(SEED_BLOGS), 8)

    def test_ctl_blog_image_asset(self):
        """Automatic CTL Line blog must use authentic /automatic-ctl.png image."""
        from api.seed_blogs import SEED_BLOGS
        ctl_blog = next((b for b in SEED_BLOGS if b["slug"] == "automatic-cut-to-length-ctl-line-guide"), None)
        self.assertIsNotNone(ctl_blog)
        self.assertEqual(ctl_blog["image"], "/automatic-ctl.png")

    def test_blog_models_validation(self):
        """Blog models must serialize and validate required fields."""
        from api.index import BlogArticleCreate
        payload = BlogArticleCreate(
            title="Test Rolling Mill Guide",
            summary="A short summary of rolling mills."
        )
        self.assertEqual(payload.title, "Test Rolling Mill Guide")
        self.assertTrue(payload.published)


if __name__ == "__main__":
    unittest.main()

