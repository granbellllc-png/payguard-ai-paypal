#!/usr/bin/env python3
"""
Unit & Integration Tests for PayGuard AI (PayPal AI Hackathon Multi-Prize Stack).
Tests PayPal Orders v2 lifecycle, AI Deliverable Audit, AG Grid serialization,
Bryntum Timeline tasks, Channel3 discovery, and APIMatic schema validation.
"""
import json
import threading
import urllib.request
import unittest
from http.server import HTTPServer
from apimatic_paypal_sdk import APIMaticPayPalClient
from server import PayGuardRequestHandler


class TestPayGuardAI(unittest.TestCase):
    def setUp(self) -> None:
        self.client = APIMaticPayPalClient()

    def test_http_server_end_to_end(self) -> None:
        httpd = HTTPServer(("127.0.0.1", 0), PayGuardRequestHandler)
        port = httpd.server_port
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/state", timeout=5) as resp:
                state = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(state["ok"])
                self.assertGreaterEqual(len(state["ag_grid_rows"]), 3)

            create_req = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/orders/create",
                data=json.dumps(
                    {
                        "buyer_email": "cfo@granbell.ae",
                        "merchant_name": "CloudCore AI Systems",
                        "description": "E2E HTTP Test Milestone",
                        "amount_usd": 1950.0,
                        "intent": "AUTHORIZE",
                        "channel3_sku": "CH3-AI-RAG-01",
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(create_req, timeout=5) as resp2:
                created = json.loads(resp2.read().decode("utf-8"))
                self.assertTrue(created["ok"])
                oid = created["order"]["order_id"]

            cap_req = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/orders/capture",
                data=json.dumps(
                    {
                        "order_id": oid,
                        "deliverable_evidence": "All unit tests pass 100%, SLA verified, SHA256 receipt ok.",
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(cap_req, timeout=5) as resp3:
                captured = json.loads(resp3.read().decode("utf-8"))
                self.assertTrue(captured["ok"])
                self.assertEqual(captured["order"]["status"], "CAPTURED")
        finally:
            httpd.shutdown()
            httpd.server_close()

    def test_initial_seed_and_kpis(self) -> None:
        kpis = self.client.get_summary_kpis()
        self.assertEqual(kpis["total_orders"], 3)
        self.assertAlmostEqual(kpis["total_volume_usd"], 16450.00)
        self.assertAlmostEqual(kpis["captured_volume_usd"], 4500.00)
        self.assertAlmostEqual(kpis["active_escrow_usd"], 11950.00)

    def test_channel3_discovery_filtering(self) -> None:
        all_items = self.client.get_channel3_catalog()
        self.assertEqual(len(all_items), 4)
        rag_items = self.client.get_channel3_catalog("RAG")
        self.assertEqual(len(rag_items), 1)
        self.assertEqual(rag_items[0]["sku"], "CH3-AI-RAG-01")

    def test_create_and_capture_agentic_order(self) -> None:
        new_order = self.client.create_agentic_order(
            buyer_email="alex@granbell.ae",
            merchant_name="Quantum Cloud Services",
            description="Milestone 4: Automated PayPal Payout Pipeline",
            amount_usd=2500.00,
            intent="AUTHORIZE",
            channel3_sku="CH3-AI-RAG-01",
        )
        self.assertEqual(new_order.status, "AUTHORIZED")
        self.assertEqual(new_order.amount_usd, 2500.00)

        captured_rec, report = self.client.audit_and_capture_order(
            order_id=new_order.order_id,
            deliverable_evidence="All 12 unit tests pass, SLA p99 < 25ms verified, sha256 receipt signed.",
        )
        self.assertEqual(captured_rec.status, "CAPTURED")
        self.assertGreaterEqual(report["ai_confidence"], 0.90)
        self.assertEqual(len(captured_rec.sha256_receipt), 64)

    def test_validation_guardrails(self) -> None:
        with self.assertRaises(ValueError):
            self.client.create_agentic_order("invalid-email", "M", "Desc", 100.0)
        with self.assertRaises(ValueError):
            self.client.create_agentic_order("a@b.com", "M", "Desc", -50.0)
        with self.assertRaises(ValueError):
            self.client.audit_and_capture_order("PAYPAL-ORD-902B", "too short")

    def test_ag_grid_and_bryntum_models(self) -> None:
        grid_rows = self.client.get_ag_grid_rows()
        bryntum_tasks = self.client.get_bryntum_timeline_tasks()
        self.assertEqual(len(grid_rows), len(bryntum_tasks))
        self.assertIn("paypalOrderId", bryntum_tasks[0])
        self.assertIn("sha256_receipt", grid_rows[0])


if __name__ == "__main__":
    unittest.main()
