"""World Bank API fetcher for Iran inflation data."""
import time
import requests
import pandas as pd
from ..config import (
    WORLD_BANK_API_BASE,
    WORLD_BANK_INDICATORS,
    API_RETRY_ATTEMPTS,
    API_RETRY_DELAY,
    REQUEST_TIMEOUT,
)


def _fetch_indicator(indicator: str, country: str = "IRN") -> list[dict]:
    """Fetch all records for a single World Bank indicator with retry logic."""
    url = f"{WORLD_BANK_API_BASE}/country/{country}/indicator/{indicator}"
    params = {"format": "json", "per_page": 500}
    records = []
    page = 1

    while True:
        for attempt in range(API_RETRY_ATTEMPTS):
            try:
                params["page"] = page
                resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                data = resp.json()
                break
            except (requests.RequestException, ValueError) as e:
                if attempt < API_RETRY_ATTEMPTS - 1:
                    time.sleep(API_RETRY_DELAY * (attempt + 1))
                else:
                    print(f"  [World Bank] Failed to fetch {indicator} page {page}: {e}")
                    return records

        if not data or len(data) < 2 or data[1] is None:
            break

        for item in data[1]:
            if item.get("value") is not None:
                records.append({
                    "year": int(item["date"]),
                    "source": "World Bank",
                    "indicator": indicator,
                    "indicator_name": WORLD_BANK_INDICATORS.get(indicator, indicator),
                    "value": float(item["value"]),
                })

        total_pages = data[0].get("pages", 1)
        if page >= total_pages:
            break
        page += 1

    return records


def fetch_world_bank() -> pd.DataFrame:
    """Fetch CPI, inflation, and food inflation data from World Bank for Iran.

    Returns a DataFrame with columns:
        year, source, indicator, indicator_name, value
    """
    print("[World Bank] Fetching Iran inflation data...")
    all_records = []

    for indicator, name in WORLD_BANK_INDICATORS.items():
        print(f"  Fetching {name} ({indicator})...")
        records = _fetch_indicator(indicator)
        all_records.extend(records)
        print(f"  Got {len(records)} records")
        time.sleep(0.5)  # Be polite to the API

    df = pd.DataFrame(all_records)
    print(f"[World Bank] Total: {len(df)} records")
    return df
