from datetime import datetime
import pandas as pd

def log_trade(symbol, entry, signal_type, pnl):
    # Appends to a CSV or PostgreSQL database for history tracking
    data = {
        "time": datetime.now(),
        "symbol": symbol,
        "type": signal_type,
        "entry": entry,
        "pnl": pnl
    }
    pd.DataFrame([data]).to_csv("trade_history.csv", mode='a', header=False)
