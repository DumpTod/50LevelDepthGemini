from fyers_apiv3.fyers_tbt import FyersDataSocket
import os

class TBTManager:
    def __init__(self, access_token):
        self.access_token = access_token
        self.symbols = ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX"]
        
    def on_message(self, message):
        # This processes the 50 bids and 50 asks
        # We calculate Order Flow Imbalance (OFI) here
        symbol = message.get('symbol')
        bids = message.get('bids', [])
        asks = message.get('asks', [])
        
        # Physics Logic: Measuring pressure
        bid_vol = sum(b[1] for b in bids)
        ask_vol = sum(a[1] for a in asks)
        pressure = (bid_vol - ask_vol) / (bid_vol + ask_vol)
        
        # Broadcast to local cache for API access
        self.latest_data[symbol] = {
            "depth": message,
            "pressure": round(pressure, 4)
        }

    def connect(self):
        fyers = FyersDataSocket(
            access_token=f"{os.environ.get('API_KEY')}:{self.access_token}",
            litemode=False # Crucial: False enables 50-level depth
        )
        fyers.on_message = self.on_message
        fyers.subscribe(symbols=self.symbols, data_type="depth")
        fyers.connect()
