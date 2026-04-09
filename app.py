from fastapi import FastAPI, WebSocket
from fyers_manager import TBTManager
import asyncio

app = FastAPI()
tbt = TBTManager(access_token="YOUR_TOKEN")

@app.on_event("startup")
async def startup():
    asyncio.create_task(tbt.connect())

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Push real-time 50-level stats to the UI
        payload = {
            "nifty": tbt.latest_data.get("NSE:NIFTY50-INDEX"),
            "banknifty": tbt.latest_data.get("NSE:NIFTYBANK-INDEX"),
            "signals": tbt.get_active_signals()
        }
        await websocket.send_json(payload)
        await asyncio.sleep(0.05) # 50ms refresh for ultra-low latency
