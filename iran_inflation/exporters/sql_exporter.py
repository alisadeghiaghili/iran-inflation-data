"""SQL Server exporter for Iran inflation data."""
import pandas as pd
from sqlalchemy import create_engine, text
from ..config import SQL_SERVER_CONNECTION


def export_sql(monthly_df: pd.DataFrame | None, yearly_df: pd.DataFrame | None) -> None:
    """Export data to SQL Server via SQLAlchemy.

    Tables created:
        - iran_inflation_monthly
        - iran_inflation_yearly
    """
    print("[SQL] Attempting SQL Server export...")

    has_monthly = monthly_df is not None and not monthly_df.empty
    has_yearly = yearly_df is not None and not yearly_df.empty

    try:
        engine = create_engine(SQL_SERVER_CONNECTION)

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("  Connected to SQL Server successfully")

        # Export monthly data
        if has_monthly:
            monthly_df.to_sql(
                "iran_inflation_monthly",
                con=engine,
                if_exists="replace",
                index=False,
                chunksize=1000,
            )
            print(f"  Exported monthly data: {len(monthly_df)} rows to 'iran_inflation_monthly'")

            # Create index
            with engine.connect() as conn:
                conn.execute(text(
                    "CREATE INDEX idx_monthly_date ON iran_inflation_monthly (date)"
                ))
                conn.commit()
            print("  Created index on iran_inflation_monthly.date")

        # Export yearly data
        if has_yearly:
            yearly_df.to_sql(
                "iran_inflation_yearly",
                con=engine,
                if_exists="replace",
                index=False,
                chunksize=1000,
            )
            print(f"  Exported yearly data: {len(yearly_df)} rows to 'iran_inflation_yearly'")

            # Create index
            with engine.connect() as conn:
                conn.execute(text(
                    "CREATE INDEX idx_yearly_year ON iran_inflation_yearly (year)"
                ))
                conn.commit()
            print("  Created index on iran_inflation_yearly.year")

        print("[SQL] SQL Server export completed successfully")

    except ImportError as e:
        print(f"  [SQL] Missing dependency: {e}")
        print("  [SQL] Install with: pip install sqlalchemy pyodbc")
        print("  [SQL] Skipping SQL Server export")
    except Exception as e:
        print(f"  [SQL] Connection failed: {e}")
        print("  [SQL] Check your connection string in src/config.py")
        print("  [SQL] Set the IRAN_INFLATION_DB_URL environment variable")
        print("  [SQL] Skipping SQL Server export")
