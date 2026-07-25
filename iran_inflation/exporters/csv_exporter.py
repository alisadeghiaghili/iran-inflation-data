"""CSV exporter for Iran inflation data."""
import os
import pandas as pd
from ..config import OUTPUT_DIR


def export_csv(monthly_df: pd.DataFrame | None, yearly_df: pd.DataFrame | None) -> None:
    """Export monthly and yearly data to CSV files.

    Files created:
        - data/processed/iran_inflation_monthly.csv
        - data/processed/iran_inflation_yearly.csv
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    monthly_path = os.path.join(OUTPUT_DIR, "iran_inflation_monthly.csv")
    yearly_path = os.path.join(OUTPUT_DIR, "iran_inflation_yearly.csv")

    if monthly_df is not None and not monthly_df.empty:
        monthly_df.to_csv(monthly_path, index=False, encoding="utf-8-sig")
        print(f"[CSV] Exported monthly data to {monthly_path} ({len(monthly_df)} rows)")
    else:
        print("[CSV] No monthly data to export")

    if yearly_df is not None and not yearly_df.empty:
        yearly_df.to_csv(yearly_path, index=False, encoding="utf-8-sig")
        print(f"[CSV] Exported yearly data to {yearly_path} ({len(yearly_df)} rows)")
    else:
        print("[CSV] No yearly data to export")
