"""Central Bank of Iran (CBI) web scraper for inflation data."""
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from ..config import (
    CBI_BASE_URL,
    CBI_SCRAPING_DELAY,
    API_RETRY_ATTEMPTS,
    API_RETRY_DELAY,
    REQUEST_TIMEOUT,
)


def _try_requests_fetch(url: str) -> str | None:
    """Try to fetch a page with requests (works if no JS rendering needed)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    for attempt in range(API_RETRY_ATTEMPTS):
        try:
            resp = requests.get(url, headers=headers, timeout=(5, REQUEST_TIMEOUT))
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            if attempt < API_RETRY_ATTEMPTS - 1:
                time.sleep(API_RETRY_DELAY)
            else:
                print(f"  [CBI] Failed to fetch {url}: {e}")
    return None


def _try_playwright_fetch(url: str) -> str | None:
    """Try to fetch a page with Playwright (for JS-rendered content)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [CBI] Playwright not installed. Install with: pip install playwright && playwright install")
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=REQUEST_TIMEOUT * 1000)
            time.sleep(2)  # Wait for dynamic content
            content = page.content()
            browser.close()
            return content
    except Exception as e:
        print(f"  [CBI] Playwright failed for {url}: {e}")
        return None


def _parse_cbi_tables(html: str) -> list[dict]:
    """Parse CPI tables from CBI HTML content."""
    records = []
    soup = BeautifulSoup(html, "lxml")

    # Look for tables containing CPI data
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        # Try to identify header row
        header_cells = rows[0].find_all(["th", "td"])
        headers = [cell.get_text(strip=True).lower() for cell in header_cells]

        # Look for date/year and value columns
        date_col = None
        value_col = None
        for i, h in enumerate(headers):
            if any(kw in h for kw in ["year", "date", "tarikh", "sal"]):
                date_col = i
            if any(kw in h for kw in ["cpi", "index", "shoae", "value"]):
                value_col = i

        if date_col is not None and value_col is not None:
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) > max(date_col, value_col):
                    date_text = cells[date_col].get_text(strip=True)
                    value_text = cells[value_col].get_text(strip=True).replace(",", "")

                    try:
                        value = float(value_text)
                    except ValueError:
                        continue

                    # Try to parse date
                    year = None
                    month = None
                    if "-" in date_text:
                        parts = date_text.split("-")
                        try:
                            year = int(parts[0])
                            month = int(parts[1]) if len(parts) > 1 else None
                        except ValueError:
                            pass
                    else:
                        try:
                            year = int(date_text)
                        except ValueError:
                            pass

                    if year:
                        records.append({
                            "year": year,
                            "month": month,
                            "date": f"{year}-{month:02d}-01" if month else f"{year}-01-01",
                            "source": "CBI",
                            "indicator": "CPI",
                            "indicator_name": "Consumer Price Index (CBI)",
                            "value": value,
                        })

    return records


def fetch_cbi() -> pd.DataFrame:
    """Fetch monthly CPI data from Central Bank of Iran.

    Attempts direct HTTP request only. If the CBI website requires
    JavaScript rendering, this will return empty data gracefully.

    Returns a DataFrame with columns:
        year, month, date, source, indicator, indicator_name, value
    """
    print("[CBI] Fetching Iran CPI data from Central Bank of Iran...")
    all_records = []

    # Try the statistics page
    stats_url = f"{CBI_BASE_URL}/en/Statistics"
    print(f"  Trying {stats_url}...")

    html = _try_requests_fetch(stats_url)
    if html:
        records = _parse_cbi_tables(html)
        all_records.extend(records)
        print(f"  Got {len(records)} records via requests")

    # Try alternative URLs
    if not all_records:
        alt_urls = [
            f"{CBI_BASE_URL}/en/section/191/cpi",
            f"{CBI_BASE_URL}/en/section/191/inflation",
            f"{CBI_BASE_URL}/en/statistics",
        ]
        for alt_url in alt_urls:
            time.sleep(CBI_SCRAPING_DELAY)
            print(f"  Trying alternative URL: {alt_url}...")
            html = _try_requests_fetch(alt_url)
            if html:
                records = _parse_cbi_tables(html)
                if records:
                    all_records.extend(records)
                    print(f"  Got {len(records)} records")
                    break

    if not all_records:
        print("  [CBI] CBI website requires JavaScript rendering.")
        print("  [CBI] To enable Playwright scraping, run: pip install playwright && playwright install")
        print("  [CBI] Continuing without CBI data...")

    df = pd.DataFrame(all_records)
    print(f"[CBI] Total: {len(df)} records")
    return df
