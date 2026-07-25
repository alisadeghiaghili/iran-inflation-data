"""IMF SDMX API fetcher for Iran inflation data."""
import time
import requests
import pandas as pd
from ..config import (
    IMF_SDMX_BASE,
    API_RETRY_ATTEMPTS,
    API_RETRY_DELAY,
    REQUEST_TIMEOUT,
)


def _parse_sdmx_json(data: dict, indicator_name: str) -> list[dict]:
    """Parse SDMX-JSON response into a list of records."""
    records = []
    try:
        datasets = data.get("dataSets", [])
        if not datasets:
            return records

        dataset = datasets[0]
        series = dataset.get("series", {})

        # Get time dimension structure
        dimensions = data.get("structure", {}).get("dimensions", {})
        time_dim = dimensions.get("observation", [])
        time_periods = [tp.get("id", "") for tp in time_dim] if time_dim else []

        for series_key, series_data in series.items():
            observations = series_data.get("observations", {})
            for time_idx, obs_values in observations.items():
                if obs_values and obs_values[0] is not None:
                    # Convert time index to date string
                    time_idx_int = int(time_idx)
                    if time_idx_int < len(time_periods):
                        period_str = time_periods[time_idx_int]
                    else:
                        period_str = str(time_idx_int)

                    # Parse period string (e.g., "2020-01" or "2020")
                    if "-" in period_str:
                        parts = period_str.split("-")
                        year = int(parts[0])
                        month = int(parts[1]) if len(parts) > 1 else None
                    else:
                        year = int(period_str)
                        month = None

                    records.append({
                        "year": year,
                        "month": month,
                        "date": f"{year}-{month:02d}-01" if month else f"{year}-01-01",
                        "source": "IMF",
                        "indicator": "ICPI",
                        "indicator_name": indicator_name,
                        "value": float(obs_values[0]),
                    })
    except (KeyError, IndexError, ValueError) as e:
        print(f"  [IMF] Error parsing SDMX response: {e}")

    return records


def fetch_imf() -> pd.DataFrame:
    """Fetch monthly CPI data from IMF for Iran via SDMX-JSON API.

    Returns a DataFrame with columns:
        year, month, date, source, indicator, indicator_name, value
    """
    print("[IMF] Fetching Iran CPI data...")
    all_records = []

    # IMF ICPI dataset for Iran
    url = f"{IMF_SDMX_BASE}/CompactData/ICPI/A.IR"
    params = {"startPeriod": "1990", "endPeriod": "2025"}

    for attempt in range(API_RETRY_ATTEMPTS):
        try:
            print(f"  Connecting to IMF API (attempt {attempt + 1})...")
            resp = requests.get(url, params=params, timeout=(5, REQUEST_TIMEOUT))
            resp.raise_for_status()
            data = resp.json()
            records = _parse_sdmx_json(data, "International Consumer Price Index")
            all_records.extend(records)
            print(f"  Got {len(records)} records from IMF")
            break
        except requests.RequestException as e:
            if attempt < API_RETRY_ATTEMPTS - 1:
                print(f"  [IMF] Request failed: {e}. Retrying...")
                time.sleep(API_RETRY_DELAY * (attempt + 1))
            else:
                print(f"  [IMF] Failed after {API_RETRY_ATTEMPTS} attempts: {e}")
                print("  [IMF] IMF data unavailable, continuing without it.")
        except ValueError as e:
            print(f"  [IMF] Failed to parse response: {e}")
            break

    df = pd.DataFrame(all_records)
    print(f"[IMF] Total: {len(df)} records")
    return df
