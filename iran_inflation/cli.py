"""CLI interface for Iran Inflation Data package."""
import sys
import os
import click
import pandas as pd

from . import __version__
from .fetchers import fetch_world_bank, fetch_imf, fetch_cbi
from .processors import process_monthly, process_yearly
from .exporters import export_csv, export_excel, export_sql
from .exporters.sql_script_exporter import export_sql_script


@click.group()
@click.version_option(version=__version__, prog_name="iran-inflation")
def main():
    """Iran Inflation Data - Fetch and export Iran inflation data."""
    pass


@main.command()
@click.option(
    "--source",
    type=click.Choice(["all", "worldbank", "imf", "cbi"]),
    default="all",
    help="Data source to fetch from",
)
@click.option(
    "--export",
    "export_format",
    type=click.Choice(["csv", "excel", "sql", "sql-script", "all"]),
    default="all",
    help="Export format",
)
@click.option("--output-dir", default="data/processed", help="Output directory")
def fetch(source, export_format, output_dir):
    """Fetch inflation data from sources and export."""
    click.echo("=" * 50)
    click.echo("Iran Inflation Data Pipeline")
    click.echo("=" * 50)

    # Fetch data
    click.echo("\n--- Fetching Data ---")
    wb_df = pd.DataFrame()
    imf_df = pd.DataFrame()
    cbi_df = pd.DataFrame()

    if source in ("all", "worldbank"):
        click.echo("Fetching from World Bank...")
        wb_df = fetch_world_bank()

    if source in ("all", "imf"):
        click.echo("Fetching from IMF...")
        try:
            imf_df = fetch_imf()
        except Exception as e:
            click.echo(f"  Warning: IMF fetch failed: {e}", err=True)

    if source in ("all", "cbi"):
        click.echo("Fetching from CBI...")
        try:
            cbi_df = fetch_cbi()
        except Exception as e:
            click.echo(f"  Warning: CBI fetch failed: {e}", err=True)

    # Process data
    click.echo("\n--- Processing Data ---")
    yearly_df = process_yearly(wb_df)
    monthly_df = process_monthly(cbi_df, imf_df)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Export
    click.echo("\n--- Exporting Data ---")
    if export_format in ("csv", "all"):
        export_csv(monthly_df, yearly_df)

    if export_format in ("excel", "all"):
        export_excel(monthly_df, yearly_df)

    if export_format in ("sql", "all"):
        export_sql(monthly_df, yearly_df)

    if export_format in ("sql-script", "all"):
        export_sql_script(monthly_df, yearly_df)

    # Summary
    click.echo("\n" + "=" * 50)
    click.echo("Pipeline Complete!")
    if not yearly_df.empty:
        click.echo(f"Yearly data: {len(yearly_df)} rows")
    if not monthly_df.empty:
        click.echo(f"Monthly data: {len(monthly_df)} rows")
    click.echo("=" * 50)


@main.command()
def indicators():
    """List available indicators and data sources."""
    click.echo("Available Data Sources and Indicators:")
    click.echo("=" * 50)

    click.echo("\n1. World Bank (Yearly)")
    click.echo("   - FP.CPI.TOTL: Consumer Price Index (2010=100)")
    click.echo("   - FP.CPI.TOTL.ZG: Inflation, consumer prices (annual %)")
    click.echo("   - FP.CPI.TOTL.FD.ZG: Food inflation (annual %)")

    click.echo("\n2. IMF (Monthly)")
    click.echo("   - ICPI: International Consumer Price Index")

    click.echo("\n3. Central Bank of Iran (Monthly)")
    click.echo("   - CPI: Consumer Price Index (requires Playwright)")

    click.echo("\nUsage:")
    click.echo("  iran-inflation fetch --source worldbank")
    click.echo("  iran-inflation fetch --source all --export csv,excel")


@main.command()
@click.option("--output", default="iran_inflation.sql", help="Output SQL file")
def generate_sql(output):
    """Generate SQL script for database import."""
    click.echo("Generating SQL script...")

    # Fetch World Bank data for SQL generation
    wb_df = fetch_world_bank()
    yearly_df = process_yearly(wb_df)

    # Generate SQL script
    from .config import OUTPUT_DIR
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    sql_path = os.path.join(OUTPUT_DIR, output)
    export_sql_script(None, yearly_df)

    click.echo(f"SQL script generated: {sql_path}")


if __name__ == "__main__":
    main()
