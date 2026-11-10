# 🛡️ PayGuard AI — Autonomous Agentic Commerce & Smart Milestone Escrow for PayPal

Built for the **PayPal AI Hackathon** (`paypalaihackathon`).

## 🚀 Overview & Problem Solved
B2B buyers, enterprises, and freelancers lose billions every year to scope creep, unverified digital deliverables, and payment disputes. **PayGuard AI** bridges **PayPal Orders v2 (`AUTHORIZE` / `CAPTURE`)** with an **Autonomous AI Deliverable Auditor**, **Channel3 SKU Discovery**, **APIMatic Type-Safe SDK Validation**, **AG Grid Live Financial Ledger**, and **Bryntum Milestone Scheduling**.

## 🏆 Sponsor Integrations Included (Multi-Prize Architecture)
1. **PayPal Developer Platform (Orders v2 & OAuth2 Sandbox):** Full authorization hold (`AUTHORIZE`), idempotency key tracking (`PayPal-Request-Id`), and automated post-audit fund capture (`/v2/checkout/orders/{id}/capture`).
2. **AG Grid (`ag-grid-community` v31):** Interactive dark-mode enterprise ledger with sorting, filtering, row selection, and real-time risk telemetry.
3. **Bryntum Scheduler/Timeline Model:** Real-time milestone window tracking and escrow completion progress bars synchronized with PayPal Order states.
4. **APIMatic Schema-Validated Client (`apimatic_paypal_sdk.py`):** Strict input/output validation, automatic Sandbox OAuth2 token lifecycle, and request latency telemetry.
5. **Channel3 Agentic Commerce Catalog:** Automated SKU discovery and B2B procurement matching with AI confidence scoring.

## ⚡ Quick Start (Zero Dependencies Required)

```bash
# 1. Run the automated unit & integration test suite
python3 -m unittest discover -v

# 2. Launch the PayGuard AI Web Server (Port 8090)
python3 server.py
```

Then open **http://127.0.0.1:8090** in your browser.
Optionally set `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` to connect directly to `https://api-m.sandbox.paypal.com`.
