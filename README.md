# iran-inflation-data

Python package to extract, process, and export Iran's monthly and yearly inflation data from World Bank, IMF, and Central Bank of Iran APIs to CSV, Excel, and SQL Server formats for prediction and analysis tasks.

## Installation

```bash
# Basic install (World Bank data only)
pip install iran-inflation-data

# With Excel support
pip install iran-inflation-data[excel]

# With SQL Server support
pip install iran-inflation-data[sql]

# With all data sources
pip install iran-inflation-data[all]

# Development install
pip install -e ".[all,dev]"
```

## Quick Start

### As a CLI tool

```bash
# Fetch all data and export to all formats
iran-inflation fetch

# Fetch only World Bank data
iran-inflation fetch --source worldbank

# Export to specific format
iran-inflation fetch --export csv,excel

# List available indicators
iran-inflation indicators

# Generate SQL script
iran-inflation generate-sql
```

### As a Python library

```python
from iran_inflation import fetch_world_bank, process_yearly, export_csv

# Fetch data from World Bank
yearly_data = fetch_world_bank()

# Process into clean DataFrame
yearly_df = process_yearly(yearly_data)

# Export to CSV
export_csv(None, yearly_df)
```

## Data Sources

| Source | Granularity | Coverage | Extra Install |
|--------|------------|----------|---------------|
| World Bank | Yearly | 1960-2025 | `pip install wbgapi` |
| IMF | Monthly | 1990-2025 | `pip install sdmx1` |
| CBI | Monthly | Varies | `pip install playwright && playwright install` |

## Available Indicators

- **CPI Index** (Consumer Price Index, 2010=100)
- **Inflation YoY %** (Year-over-year inflation rate)
- **Food Inflation %** (Food-specific inflation)

## Output Files

After running the pipeline:

- `data/processed/iran_inflation_yearly.csv` - Yearly data
- `data/processed/iran_inflation_monthly.csv` - Monthly data (if available)
- `data/processed/iran_inflation.xlsx` - Excel workbook with multiple sheets
- `data/processed/iran_inflation.sql` - SQL Server script

## Configuration

### SQL Server Connection

Set the `IRAN_INFLATION_DB_URL` environment variable:

```bash
# Windows
set IRAN_INFLATION_DB_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server

# Linux/Mac
export IRAN_INFLATION_DB_URL="mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server"
```

Or edit `src/config.py` directly.

## Project Structure

```
iran_inflation/
├── __init__.py          # Package exports
├── __main__.py          # python -m iran_inflation
├── cli.py               # Click CLI
├── config.py            # Configuration
├── fetchers/
│   ├── world_bank.py    # World Bank API
│   ├── imf.py           # IMF SDMX API
│   └── cbi.py           # Central Bank of Iran
├── processors/
│   └── cleaner.py       # Data cleaning
└── exporters/
    ├── csv_exporter.py
    ├── excel_exporter.py
    ├── sql_exporter.py
    └── sql_script_exporter.py
```

## Data Schema

### Yearly Data

| Column | Type | Description |
|--------|------|-------------|
| year | INT | Year of observation |
| cpi_index | FLOAT | Consumer Price Index (2010=100) |
| inflation_yoy_pct | FLOAT | Year-over-year inflation rate (%) |
| food_inflation_pct | FLOAT | Food inflation rate (%) |
| source | STRING | Data source (World Bank) |

### Monthly Data

| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Date (YYYY-MM-DD) |
| year | INT | Year |
| month | INT | Month (1-12) |
| cpi_index | FLOAT | Consumer Price Index value |
| source | STRING | Data source (CBI or IMF) |

## Requirements

- Python 3.10+
- See `requirements.txt` or `pyproject.toml` for dependencies

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [World Bank API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392)
- [IMF Data Services](https://data.imf.org/)
- [Central Bank of Iran](https://www.cbi.ir/)
