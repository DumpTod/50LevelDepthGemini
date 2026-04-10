import os
import asyncio
import json
import numpy as np
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fyers_apiv3.FyersWebsocket import data_ws

app = FastAPI()

# Configuration
API_KEY = os.environ.get('API_KEY', 'VS55VDHYCW-100')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN') # Ensure this is set in Railway env
SYMBOLS = ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX"]

# Shared State
market_data = {
    "NSE:NIFTY50-INDEX": {"depth": {"bids": [], "asks": []}, "ofi": 0, "signal": "WAIT"},
    "NSE:NIFTYBANK-INDEX": {"depth": {"bids": [], "asks": []}, "ofi": 0, "signal": "WAIT"}
}
trade_history = []

def calculate_physics_stats(message):
    """Calculates Order Flow Imbalance and Velocity."""
    bids = message.get('bids', [])
    asks = message.get('asks', [])
    if not bids or not asks: return 0, "WAIT"

    # 1. Order Flow Imbalance (OFI)
    bid_vol = sum(b[1] for b in bids)
    ask_vol = sum(a[1] for a in asks)
    ofi = (bid_vol - ask_vol) / (bid_vol + ask_vol)

    # 2. Signal Logic
    signal = "WAIT"
    if ofi > 0.75: signal = "STRONG BUY"
    elif ofi < -0.75: signal = "STRONG SELL"
    
    return round(ofi, 4), signal

def on_message(message):
    sym = message.get('symbol')
    if sym in market_data:
        ofi, signal = calculate_physics_stats(message)
        market_data[sym]["depth"] = {"bids": message['bids'][:50], "asks": message['asks'][:50]}
        market_data[sym]["ofi"] = ofi
        market_data[sym]["signal"] = signal
        
        # Log 2-3 high probability trades per day
        if signal != "WAIT" and len(trade_history) < 3:
            if not any(t['symbol'] == sym for t in trade_history):
                trade_history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "symbol": sym,
                    "signal": signal,
                    "price": message['bids'][0][0] if "BUY" in signal else message['asks'][0][0]
                })

# Serve Dashboard
@app.get("/")
async def get_dashboard():
    return FileResponse("index.html")

# WebSocket for Real-time Updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Initialize Fyers TBT in background if not started
        while True:
            payload = {
                "market": market_data,
                "history": trade_history
            }
            await websocket.send_json(payload)
            await asyncio.sleep(0.1) # 100ms refresh
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    import uvicorn
    # Fyers TBT setup
    tbt = data_ws.FyersDataSocket(access_token=f"{API_KEY}:{ACCESS_TOKEN}", litemode=False)
    tbt.on_message = on_message
    tbt.subscribe(symbols=SYMBOLS, data_type="depth")
    # Run TBT in a separate thread/task
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, tbt.connect)
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
