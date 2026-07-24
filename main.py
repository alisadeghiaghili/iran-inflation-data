"""Iran Inflation Data Extraction Pipeline.

Fetches monthly and yearly inflation data from World Bank, IMF, and CBI,
then exports to CSV, Excel, and SQL Server formats.
"""
import sys
import os
import signal
from contextlib import contextmanager

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.fetchers import fetch_world_bank, fetch_imf, fetch_cbi
from src.processors import process_monthly, process_yearly
from src.exporters import export_csv, export_excel, export_sql
from src.exporters.sql_script_exporter import export_sql_script


class TimeoutError(Exception):
    pass


@contextmanager
def timeout(seconds):
    """Context manager for timeout (Unix only, no-op on Windows)."""
    if sys.platform == "win32":
        # Windows doesn't support SIGALRM; just yield
        yield
        return

    def signal_handler(signum, frame):
        raise TimeoutError("Timed out")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def main():
    """Run the full data extraction pipeline."""
    print("=" * 60)
    print("Iran Inflation Data Extraction Pipeline")
    print("=" * 60)

    # 1. Fetch data from all sources
    print("\n--- Fetching Data ---")
    wb_df = fetch_world_bank()

    # IMF - skip if unreachable
    try:
        with timeout(15):
            imf_df = fetch_imf()
    except (TimeoutError, Exception) as e:
        print(f"[IMF] Skipped due to timeout: {e}")
        import pandas as pd
        imf_df = pd.DataFrame()

    # CBI - skip if unreachable
    try:
        with timeout(15):
            cbi_df = fetch_cbi()
    except (TimeoutError, Exception) as e:
        print(f"[CBI] Skipped due to timeout: {e}")
        import pandas as pd
        cbi_df = pd.DataFrame()

    # 2. Process and merge data
    print("\n--- Processing Data ---")
    yearly_df = process_yearly(wb_df)
    monthly_df = process_monthly(cbi_df, imf_df)

    # 3. Export to all formats
    print("\n--- Exporting Data ---")
    export_csv(monthly_df, yearly_df)
    export_excel(monthly_df, yearly_df)
    export_sql(monthly_df, yearly_df)
    export_sql_script(monthly_df, yearly_df)

    # 4. Summary
    print("\n" + "=" * 60)
    print("Pipeline Summary")
    print("=" * 60)
    if not yearly_df.empty:
        print(f"Yearly data: {len(yearly_df)} rows ({int(yearly_df['year'].min())}-{int(yearly_df['year'].max())})")
    else:
        print("Yearly data: No data available")

    if not monthly_df.empty:
        print(f"Monthly data: {len(monthly_df)} rows ({monthly_df['date'].min().strftime('%Y-%m')} to {monthly_df['date'].max().strftime('%Y-%m')})")
    else:
        print("Monthly data: No data available")

    print("\nOutput files:")
    print("  - data/processed/iran_inflation_monthly.csv")
    print("  - data/processed/iran_inflation_yearly.csv")
    print("  - data/processed/iran_inflation.xlsx")
    print("  - SQL Server tables (if configured)")
    print("=" * 60)


if __name__ == "__main__":
    main()
