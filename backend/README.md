# ACM Switchover API (FastAPI)

## Endpoints
- `GET /health` – liveness
- `GET /ready` – readiness
- `WS /ws/switchovers/{operation_id}` – progress streaming (heartbeat placeholder)

## Run locally
```
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```
