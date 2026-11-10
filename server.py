#!/usr/bin/env python3
"""
PayGuard AI — Web Application & REST API Server for PayPal AI Hackathon.
Integrates PayPal Orders v2, AG Grid, Bryntum Timeline, APIMatic SDK & Channel3.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from apimatic_paypal_sdk import APIMaticPayPalClient

CLIENT = APIMaticPayPalClient()
BASE_DIR = Path(__file__).resolve().parent


class PayGuardRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            html_bytes = (BASE_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.end_headers()
            self.wfile.write(html_bytes)
            return

        if parsed.path == "/api/state":
            qs = parse_qs(parsed.query)
            q = (qs.get("q") or [""])[0]
            self._send_json(
                200,
                {
                    "ok": True,
                    "kpis": CLIENT.get_summary_kpis(),
                    "ag_grid_rows": CLIENT.get_ag_grid_rows(),
                    "bryntum_tasks": CLIENT.get_bryntum_timeline_tasks(),
                    "channel3_catalog": CLIENT.get_channel3_catalog(q),
                    "apimatic_telemetry": CLIENT.api_telemetry[:15],
                },
            )
            return

        self._send_json(404, {"ok": False, "error": "Not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        body_raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            data = json.loads(body_raw)
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "Invalid JSON body"})
            return

        try:
            if parsed.path == "/api/orders/create":
                rec = CLIENT.create_agentic_order(
                    buyer_email=str(data.get("buyer_email", "cfo@granbell.ae")),
                    merchant_name=str(data.get("merchant_name", "CloudCore AI Systems")),
                    description=str(data.get("description", "AI Agentic Milestone Order")),
                    amount_usd=float(data.get("amount_usd", 2500.0)),
                    intent=str(data.get("intent", "AUTHORIZE")),
                    channel3_sku=str(data.get("channel3_sku", "CH3-AI-RAG-01")),
                )
                self._send_json(201, {"ok": True, "order": asdict(rec), "kpis": CLIENT.get_summary_kpis()})
                return

            if parsed.path == "/api/orders/capture":
                rec, report = CLIENT.audit_and_capture_order(
                    order_id=str(data.get("order_id", "")),
                    deliverable_evidence=str(
                        data.get(
                            "deliverable_evidence",
                            "Automated unit test suite 100% pass, SLA verified, SHA256 receipt confirmed.",
                        )
                    ),
                )
                self._send_json(
                    200,
                    {"ok": True, "order": asdict(rec), "audit_report": report, "kpis": CLIENT.get_summary_kpis()},
                )
                return
        except Exception as exc:
            self._send_json(400, {"ok": False, "error": str(exc)})
            return

        self._send_json(404, {"ok": False, "error": "Endpoint not found"})


def run_server(port: int = 8090) -> None:
    server = HTTPServer(("127.0.0.1", port), PayGuardRequestHandler)
    print(f"PayGuard AI Server listening on http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server(int(os.environ.get("PORT", "8090")))
