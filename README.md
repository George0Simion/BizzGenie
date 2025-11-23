# BizzGenie

AI-powered co-pilot for small restaurant owners. The project wires together multiple lightweight services (inventory, finance, legal) behind an orchestrator, exposes them through a proxy for the React UI, and persists state in SQLite.

## Architecture
- Orchestrator (`orchestrator.py`, :5001) — Receives natural language, keeps short chat context, decides which agents to call, and immediately forwards a chat reply to the proxy.
- Inventory agent (`agents/inventory_agent.py`, :5002) — Uses an LLM to parse add/consume stock intents and writes to `db/inventory.db`.
- Finance service (`backend/financeAPI.py` via Uvicorn on :5004) — Wraps finance logic from `agents/finance_agent.py` and `agents/finance_insights.py` over SQLite (`db/finance.db`).
- Legal agent (`legal.py`, :5006) — Runs deep legal research with strict JSON output and streams results back to the orchestrator.
- Proxy (`frontEnd/backend/proxy.py`, :5000) — Gateway between React and the orchestrator; also polls inventory for UI updates.
- Frontend (`frontEnd/bizgenie-ui`) — Vite + React + Tailwind UI with chat, dashboard, inventory, finance, and legal views.

## Repo map
- `orchestrator.py`, `send_message_orchestrator.py`, `orchestrator2.py` — Orchestrator variants (use `orchestrator.py`).
- `agents/` — Inventory + finance agents and LLM client.
- `backend/financeAPI.py` — FastAPI wrapper for finance endpoints.
- `db/` — SQLite DBs plus read/write helpers.
- `frontEnd/backend/` — Flask proxy and a small simulator.
- `frontEnd/bizgenie-ui/` — React app.
- `tests/` — End-to-end runner plus finance insight tests.

## Requirements
- Python 3.10+
- Node.js 18+ and npm
- SQLite (built-in with Python)
- Environment:
  - `OPENAI_API_KEY` (OpenRouter key, used by orchestrator, inventory, finance, and legal)
  - Optional: `FINANCE_DB_PATH` to point to a custom finance DB; `VITE_PROXY_URL` for the frontend (defaults to `http://localhost:5000/api`).

## Backend setup
1) Create a virtualenv and install Python deps:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install flask flask-cors fastapi uvicorn requests pydantic pytest
```

2) Initialize the finance DB (one-time; inventory DB is created by the agent on start):
```bash
python - <<'PY'
from db.finance_db import init_db
init_db()
print("finance.db ready")
PY
```

## Run the stack (separate terminals)
1) Inventory agent (port 5002):
```bash
source .venv/bin/activate
python agents/inventory_agent.py
```

2) Legal agent (port 5006):
```bash
source .venv/bin/activate
python legal.py
```

3) Finance API (port 5004):
```bash
source .venv/bin/activate
uvicorn backend.financeAPI:app --reload --port 5004
```

4) Orchestrator (port 5001):
```bash
source .venv/bin/activate
python orchestrator.py
```

5) Proxy for the UI (port 5000):
```bash
source .venv/bin/activate
python frontEnd/backend/proxy.py
```

6) Frontend (Vite dev server, defaults to :5173):
```bash
cd frontEnd/bizgenie-ui
npm install
# Optional if the proxy runs elsewhere:
# export VITE_PROXY_URL=http://localhost:5000/api
npm run dev
```

Tip: if you only need mocked inventory/feed data for the UI, you can run `frontEnd/backend/simulator.py` (posts updates to the proxy webhook at :5000/internal/receive).

## Key endpoints
- Proxy → Orchestrator: `POST http://localhost:5000/api/chat` with `{ "message": "...", "context": {} }`.
- Orchestrator → Proxy (async): `POST /from_orchestrator` with `chatbox_response` or `data_update` payloads; the UI polls `/api/updates`.
- Inventory: `POST http://localhost:5002/inventory/message` with `{ "message": "I bought 5kg tomatoes" }`; `GET /inventory` returns stock.
- Finance (via FastAPI): `POST /api/finance/auto_check`, `POST /api/finance/message` with `{ "message": "Why did profit drop?" }`, `POST /api/finance/record_purchase`, `POST /api/finance/set_daily_profit`.
- Legal: `POST http://localhost:5006/input` with a payload containing a `legal` block (subject + context); research results are forwarded back to the orchestrator.
- Orchestrator utility: `GET http://localhost:5001/get-inventory` proxies inventory for debugging.

## Frontend notes
- The UI keeps chat, notifications, inventory, and legal tasks in `BusinessContext`.
- It polls the proxy every 2s (`/api/updates`) for `chat_message`, `data_update` (inventory/legal), and `notification` packets.
- Chat replies are shown immediately from orchestrator `chatbox_response` messages even while background agent calls finish.

## Testing
- `python tests/test.py` auto-starts inventory (5002), a legal placeholder (5003), orchestrator (5001), and the finance API (5004), then runs pytest. This calls real LLMs and may incur cost; ensure `OPENAI_API_KEY` is set.
- To run only pure Python finance insight checks (no HTTP, cheap):
```bash
pytest tests/test.py -k "compute_trend or collect_finance_insights"
```
- The test `test_finance_auto_check_http` expects the finance service to be reachable on :5004 if you run pytest directly without the helper script.

## Data
- Inventory data lives in `db/inventory.db`, finance data in `db/finance.db`. Both are SQLite and auto-created if missing. Delete the files to reset.
- `legal_latest.json` stores the last legal research response for debugging.

## Operational tips
- Orchestrator and agents respond in Romanian by default.
- All services are local HTTP; adjust ports in `comms.py` and the proxy if you change them.
- Network access is required for LLM calls (OpenRouter); without `OPENAI_API_KEY` the orchestrator/inventory/legal/finance LLM paths will fail.
