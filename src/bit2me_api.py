from __future__ import annotations
import os
import requests
import pandas as pd

BASE_URL = os.getenv("BIT2ME_BASE_URL", "https://api.bit2me.com")
API_KEY = os.getenv("BIT2ME_API_KEY")
API_SECRET = os.getenv("BIT2ME_API_SECRET")

def get_balances() -> pd.DataFrame | None:
    if not API_KEY:
        return None
    url = f"{BASE_URL}/v1/account/balances"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    items = data.get("balances", []) if isinstance(data, dict) else []
    return pd.DataFrame(items)
