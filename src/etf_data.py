from __future__ import annotations
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

def _annualized_vol(returns: pd.Series, window: int = 30) -> pd.Series:
    return returns.rolling(window).std() * np.sqrt(252)

def fetch_etf_metrics(tickers: list[str], lookback_days: int = 60, vol_window: int = 30) -> pd.DataFrame:
    end = datetime.utcnow()
    start = end - timedelta(days=lookback_days + vol_window + 5)

    data = []
    for t in tickers:
        hist = yf.Ticker(t).history(start=start.date(), end=end.date(), interval="1d")
        if hist.empty:
            continue
        hist = hist.dropna(subset=["Close"])
        hist["ret"] = hist["Close"].pct_change()
        hist["ann_vol"] = _annualized_vol(hist["ret"], window=vol_window)
        latest = hist.iloc[-1]
        row = {
            "ticker": t,
            "close": float(latest["Close"]),
            "day_change_%": float(latest["ret"] * 100) if not np.isnan(latest["ret"]) else None,
            f"ann_vol_{vol_window}d": float(latest["ann_vol"]) if not np.isnan(latest["ann_vol"]) else None,
            "n_days": int(len(hist)),
        }
        data.append(row)
    df = pd.DataFrame(data).sort_values(by=f"ann_vol_{vol_window}d", ascending=False)
    return df
