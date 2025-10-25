import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import yaml

from src.etf_data import fetch_etf_metrics
from src.bit2me_api import get_balances
from src.report import build_html_report

def load_settings(path: str = "config/settings.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def ensure_dirs(dirs):
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def iso_date():
    return datetime.now().strftime("%Y-%m-%d")

if __name__ == "__main__":
    load_dotenv()
    settings = load_settings()
    data_dir = settings["output"]["data_dir"]
    reports_dir = settings["output"]["reports_dir"]
    ensure_dirs([data_dir, reports_dir])

    etf_df = fetch_etf_metrics(
        settings["etfs"]["tickers"],
        lookback_days=settings["etfs"]["lookback_days"],
        vol_window=settings["etfs"]["vol_window"],
    )
    etf_df.to_csv(Path(data_dir) / f"etf_metrics_{iso_date()}.csv", index=False)

    b2m_df = None
    try:
        b2m_df = get_balances()
        if b2m_df is not None and not b2m_df.empty:
            b2m_df.to_csv(Path(data_dir) / f"bit2me_balances_{iso_date()}.csv", index=False)
    except Exception as e:
        print(f"Bit2Me fetch skipped: {e}")

    html = build_html_report(
        title=settings["reports"]["title"],
        etf_metrics=etf_df,
        bit2me_balances=b2m_df,
    )
    with open(Path(reports_dir) / "latest.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved: reports/latest.html")
