"""Check both contact handlers without starting clients or sending real email."""
import ast
import asyncio
import time
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Optional, Tuple
from unittest.mock import AsyncMock, Mock

from fastapi import HTTPException, Request
from pydantic import BaseModel, EmailStr, Field


ROOT = Path(__file__).resolve().parents[1]


def load_contact_handler(path):
    names = {"ContactLead", "ContactLeadCreate", "submit_contact"}
    definitions = []
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, (ast.ClassDef, ast.AsyncFunctionDef)) and node.name in names:
            node.decorator_list = []
            definitions.append(node)
    collection = SimpleNamespace(insert_one=AsyncMock(return_value=SimpleNamespace(acknowledged=True)))
    namespace = {
        "BaseModel": BaseModel, "EmailStr": EmailStr, "Field": Field, "Optional": Optional,
        "datetime": datetime, "timezone": timezone, "uuid": uuid, "time": time,
        "Request": Request, "HTTPException": HTTPException,
        "logger": Mock(),
        "db": {"contact_leads": collection}, "_mem_leads": [], "_rate_limit_map": {},
        "send_lead_email_with_diagnostics": AsyncMock(return_value=("provider-id", None)),
    }
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def load_email_helper(path):
    definition = next(node for node in ast.parse(path.read_text()).body
                      if isinstance(node, ast.AsyncFunctionDef) and node.name == "send_lead_email_with_diagnostics")
    namespace = {
        "ContactLead": SimpleNamespace, "Optional": Optional, "Tuple": Tuple,
        "os": SimpleNamespace(environ={"RESEND_API_KEY": "test-provider-key"}),
        "resend": SimpleNamespace(api_key=None, Emails=SimpleNamespace(send=Mock(return_value={"id": "sdk-id"}))),
        "requests": SimpleNamespace(post=Mock(return_value=SimpleNamespace(status_code=201, json=lambda: {"id": "rest-id"}))),
        "SENDER_EMAIL": "sender@example.com", "BUSINESS_EMAIL": "business@example.com",
        "asyncio": asyncio, "logger": Mock(), "build_lead_email_html": lambda lead: "Test email",
    }
    exec(compile(ast.Module(body=[definition], type_ignores=[]), str(path), "exec"), namespace)
    return namespace


class ContactDeliveryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.backends = [(path, load_contact_handler(ROOT / path)) for path in ("api/index.py", "backend/server.py")]
        self.request = Request({"type": "http", "client": ("192.0.2.1", 1234)})

    def payload(self, backend, **overrides):
        return backend["ContactLeadCreate"](**{
            "name": "Test buyer", "email": "buyer@example.com", "phone": "1234567890",
            "message": "Please quote a machine.", **overrides,
        })

    async def test_success_with_both_channels(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                result = await backend["submit_contact"](self.payload(backend), self.request)
                self.assertEqual(result["status"], "success")
                self.assertTrue(result["email_sent"])
                self.assertEqual(result["email_id"], "provider-id")
                self.assertIsNone(result["email_error"])
                saved = backend["db"]["contact_leads"].insert_one.call_args.args[0]
                self.assertEqual(result["lead_id"], saved["id"])
                self.assertEqual(backend["_mem_leads"][0]["id"], saved["id"])

    async def test_db_acceptance_preserves_lead_when_email_fails(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["send_lead_email_with_diagnostics"].return_value = (None, "Provider unavailable")
                result = await backend["submit_contact"](self.payload(backend), self.request)
                self.assertEqual(result["status"], "success")
                self.assertFalse(result["email_sent"])
                self.assertEqual(result["email_error"], "Provider unavailable")
                self.assertEqual(len(backend["_mem_leads"]), 1)

    async def test_email_acceptance_when_database_fails_or_is_absent(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["db"]["contact_leads"].insert_one.side_effect = RuntimeError("Storage unavailable")
                result = await backend["submit_contact"](self.payload(backend), self.request)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["email_id"], "provider-id")
                backend["db"] = None
                result = await backend["submit_contact"](self.payload(backend), self.request)
                self.assertEqual(result["status"], "success")
                self.assertEqual(len(backend["_mem_leads"]), 2)

    async def test_no_channel_acceptance_returns_503_without_phantom_cache(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["send_lead_email_with_diagnostics"].return_value = (None, "Email not configured")
                backend["db"]["contact_leads"].insert_one.side_effect = RuntimeError("Storage unavailable")
                for database in (backend["db"], None):
                    backend["db"] = database
                    with self.assertRaises(HTTPException) as caught:
                        await backend["submit_contact"](self.payload(backend), self.request)
                    self.assertEqual(caught.exception.status_code, 503)
                    self.assertIn("retry", caught.exception.detail.lower())
                    self.assertIn("contact", caught.exception.detail.lower())
                    self.assertEqual(backend["_mem_leads"], [])

    async def test_unacknowledged_db_write_is_not_acceptance(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["db"]["contact_leads"].insert_one.return_value = SimpleNamespace(acknowledged=False)
                backend["send_lead_email_with_diagnostics"].return_value = (None, "Provider unavailable")
                with self.assertRaises(HTTPException) as caught:
                    await backend["submit_contact"](self.payload(backend), self.request)
                self.assertEqual(caught.exception.status_code, 503)
                self.assertEqual(backend["_mem_leads"], [])

    async def test_unexpected_email_exception_does_not_lose_saved_lead_or_fake_success(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["send_lead_email_with_diagnostics"].side_effect = RuntimeError("Unexpected provider failure")
                result = await backend["submit_contact"](self.payload(backend), self.request)
                self.assertEqual(result["status"], "success")
                self.assertFalse(result["email_sent"])
                backend["db"] = None
                with self.assertRaises(HTTPException) as caught:
                    await backend["submit_contact"](self.payload(backend), self.request)
                self.assertEqual(caught.exception.status_code, 503)
                self.assertEqual(len(backend["_mem_leads"]), 1)

    async def test_honeypot_retains_existing_response_without_channel_attempts(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                result = await backend["submit_contact"](self.payload(backend, website_hp="bot"), self.request)
                self.assertEqual(result["email_id"], "hp_trap")
                backend["db"]["contact_leads"].insert_one.assert_not_awaited()
                backend["send_lead_email_with_diagnostics"].assert_not_awaited()
                self.assertEqual(backend["_mem_leads"], [])
                self.assertEqual(backend["_rate_limit_map"], {})

    async def test_rate_limit_still_blocks_sixth_request_before_delivery(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                for _ in range(5):
                    await backend["submit_contact"](self.payload(backend), self.request)
                with self.assertRaises(HTTPException) as caught:
                    await backend["submit_contact"](self.payload(backend), self.request)
                self.assertEqual(caught.exception.status_code, 429)
                self.assertEqual(backend["db"]["contact_leads"].insert_one.await_count, 5)
                self.assertEqual(backend["send_lead_email_with_diagnostics"].await_count, 5)


class EmailAcceptanceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.backends = [(path, load_email_helper(ROOT / path)) for path in ("api/index.py", "backend/server.py")]
        self.lead = SimpleNamespace(name="Test buyer", product_interest="Machine", email="buyer@example.com")

    async def test_sdk_requires_nonempty_confirmation_id(self):
        for path, backend in self.backends:
            for response in ({}, {"id": None}, {"id": ""}, {"id": " "}, {"id": 1}, None, "arbitrary", object()):
                with self.subTest(backend=path, sdk_response=type(response).__name__):
                    backend["resend"].Emails.send.return_value = response
                    result = await backend["send_lead_email_with_diagnostics"](self.lead)
                    self.assertEqual(result, ("rest-id", None))
            self.assertEqual(backend["requests"].post.call_count, 8)

    async def test_sdk_dict_and_known_id_attribute_are_accepted(self):
        for path, backend in self.backends:
            for response in ({"id": " sdk-id "}, SimpleNamespace(id="sdk-id")):
                with self.subTest(backend=path, sdk_response=type(response).__name__):
                    backend["resend"].Emails.send.return_value = response
                    result = await backend["send_lead_email_with_diagnostics"](self.lead)
                    self.assertEqual(result, ("sdk-id", None))
                    backend["requests"].post.assert_not_called()

    async def test_rest_2xx_without_confirmation_id_is_not_success(self):
        for path, backend in self.backends:
            backend["resend"].Emails.send.side_effect = RuntimeError("Provider failure")
            for response in ({}, {"id": None}, {"id": ""}, {"id": " "}, {"id": 1}, [], None):
                with self.subTest(backend=path, rest_response=type(response).__name__):
                    backend["requests"].post.return_value = SimpleNamespace(status_code=200, json=lambda: response)
                    email_id, error = await backend["send_lead_email_with_diagnostics"](self.lead)
                    self.assertIsNone(email_id)
                    self.assertIn("confirmation ID", error)

    async def test_rest_confirmed_id_succeeds_after_sdk_failure(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["resend"].Emails.send.side_effect = RuntimeError("Provider failure")
                self.assertEqual(await backend["send_lead_email_with_diagnostics"](self.lead), ("rest-id", None))
                self.assertNotIn("verify", backend["requests"].post.call_args.kwargs)

    async def test_rest_http_error_or_exception_is_not_success(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["resend"].Emails.send.side_effect = RuntimeError("Provider failure")
                backend["requests"].post.return_value = SimpleNamespace(status_code=503, text="Unavailable")
                self.assertIsNone((await backend["send_lead_email_with_diagnostics"](self.lead))[0])
                backend["requests"].post.side_effect = RuntimeError("Connection unavailable")
                self.assertIsNone((await backend["send_lead_email_with_diagnostics"](self.lead))[0])

    async def test_missing_email_configuration_makes_no_external_attempt(self):
        for path, backend in self.backends:
            with self.subTest(backend=path):
                backend["os"].environ.clear()
                email_id, error = await backend["send_lead_email_with_diagnostics"](self.lead)
                self.assertIsNone(email_id)
                self.assertIn("not configured", error)
                backend["resend"].Emails.send.assert_not_called()
                backend["requests"].post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
