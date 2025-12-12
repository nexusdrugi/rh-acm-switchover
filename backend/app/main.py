from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio

app = FastAPI()


class Health(BaseModel):
    status: str


@app.get("/health")
def health():
    return JSONResponse(content=Health(status="ok").model_dump())


@app.get("/ready")
def ready():
    return JSONResponse(content=Health(status="ready").model_dump())


@app.websocket("/ws/switchovers/{operation_id}")
async def ws_progress(websocket: WebSocket, operation_id: str):
    await websocket.accept()
    try:
        # Placeholder: send heartbeat until integrated with K8s pod log tail
        while True:
            await websocket.send_json(
                {
                    "type": "heartbeat",
                    "operation_id": operation_id,
                    "timestamp": asyncio.get_event_loop().time(),
                }
            )
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        return
