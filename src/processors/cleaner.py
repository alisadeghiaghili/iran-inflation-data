"""Data cleaning and standardization for Iran inflation data."""
import pandas as pd
import numpy as np


def process_yearly(wb_df: pd.DataFrame) -> pd.DataFrame:
    """Process World Bank yearly data into a clean yearly dataset.

    Returns DataFrame with columns:
        year, cpi_index, inflation_yoy_pct, food_inflation_pct, source
    """
    if wb_df.empty:
        return pd.DataFrame()

    print("[Processor] Processing yearly data...")

    # Pivot indicators into columns
    pivot = wb_df.pivot_table(
        index="year",
        columns="indicator",
        values="value",
        aggfunc="first",
    ).reset_index()

    # Rename columns to friendly names
    rename_map = {
        "FP.CPI.TOTL": "cpi_index",
        "FP.CPI.TOTL.ZG": "inflation_yoy_pct",
        "FP.CPI.TOTL.FD.ZG": "food_inflation_pct",
    }
    pivot.rename(columns=rename_map, inplace=True)

    # Add source column
    pivot["source"] = "World Bank"

    # Sort by year
    pivot.sort_values("year", inplace=True)
    pivot.reset_index(drop=True, inplace=True)

    # Ensure all expected columns exist
    for col in ["cpi_index", "inflation_yoy_pct", "food_inflation_pct"]:
        if col not in pivot.columns:
            pivot[col] = np.nan

    # Select and order columns
    result = pivot[["year", "cpi_index", "inflation_yoy_pct", "food_inflation_pct", "source"]]

    print(f"[Processor] Yearly data: {len(result)} rows, {result['year'].min()}-{result['year'].max()}")
    return result


def process_monthly(cbi_df: pd.DataFrame, imf_df: pd.DataFrame) -> pd.DataFrame:
    """Process and merge monthly data from CBI and IMF sources.

    Priority: CBI > IMF (CBI is more authoritative for Iran)

    Returns DataFrame with columns:
        date, year, month, cpi_index, source
    """
    print("[Processor] Processing monthly data...")

    frames = []

    # Process CBI data (highest priority)
    if not cbi_df.empty:
        cbi_monthly = cbi_df[["date", "year", "month", "value", "source"]].copy()
        cbi_monthly.rename(columns={"value": "cpi_index"}, inplace=True)
        frames.append(cbi_monthly)
        print(f"  CBI: {len(cbi_monthly)} monthly records")

    # Process IMF data (fallback)
    if not imf_df.empty:
        imf_monthly = imf_df[["date", "year", "month", "value", "source"]].copy()
        imf_monthly.rename(columns={"value": "cpi_index"}, inplace=True)
        frames.append(imf_monthly)
        print(f"  IMF: {len(imf_monthly)} monthly records")

    if not frames:
        print("  No monthly data available from any source")
        return pd.DataFrame()

    # Combine all sources
    combined = pd.concat(frames, ignore_index=True)

    # Ensure date column is proper datetime
    combined["date"] = pd.to_datetime(combined["date"], errors="coerce")
    combined.dropna(subset=["date"], inplace=True)

    # Ensure numeric values
    combined["cpi_index"] = pd.to_numeric(combined["cpi_index"], errors="coerce")

    # Sort by date
    combined.sort_values("date", inplace=True)

    # Remove duplicates (keep first = highest priority source)
    combined.drop_duplicates(subset=["date"], keep="first", inplace=True)

    # Add month column if missing
    combined["month"] = combined["date"].dt.month
    combined["year"] = combined["date"].dt.year

    combined.reset_index(drop=True, inplace=True)

    print(f"[Processor] Monthly data: {len(combined)} rows, {combined['date'].min()} to {combined['date'].max()}")
    return combined
