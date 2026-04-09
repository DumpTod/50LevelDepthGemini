from fastapi import FastAPI, WebSocket
from fyers_apiv3.fyers_tbt import FyersDataSocket
import os, json, asyncio

app = FastAPI()

# State management for both symbols
market_state = {
    "NSE:NIFTY50-INDEX": {"depth": {}, "ofi": 0, "signal": None},
    "NSE:NIFTYBANK-INDEX": {"depth": {}, "ofi": 0, "signal": None}
}

def on_tbt_message(message):
    sym = message.get('symbol')
    if sym in market_state:
        bids = message.get('bids', [])
        asks = message.get('asks', [])
        
        # OFI Math: (Sum of Bids - Sum of Asks) / Total
        b_vol = sum(b[1] for b in bids)
        a_vol = sum(a[1] for a in asks)
        ofi = (b_vol - a_vol) / (b_vol + a_vol) if (b_vol + a_vol) > 0 else 0
        
        market_state[sym]["depth"] = {"bids": bids[:50], "asks": asks[:50]}
        market_state[sym]["ofi"] = round(ofi, 4)

@app.websocket("/ws/data")
async def stream_data(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Send updated state to Railway frontend
        await websocket.send_json(market_state)
        await asyncio.sleep(0.1) # 10 tick/sec refresh
