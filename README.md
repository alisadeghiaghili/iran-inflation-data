# iran-inflation-data

Python pipeline to extract, process, and export Iran's monthly and yearly inflation data from World Bank, IMF, and Central Bank of Iran APIs to CSV, Excel, and SQL Server formats for prediction and analysis tasks.

## Features

- **Multi-source data collection**: World Bank API, IMF SDMX API, and Central Bank of Iran
- **Flexible export**: CSV, Excel (.xlsx), and SQL Server (via SQLAlchemy)
- **Retry logic**: Automatic retries with exponential backoff for API calls
- **Graceful degradation**: Skips unavailable sources and continues with available data

## Data Sources

| Source | Granularity | Coverage | Status |
|--------|------------|----------|--------|
| World Bank | Yearly | 1960-2025 | Working |
| IMF | Monthly | 1990-2025 | Requires network access |
| CBI | Monthly | Varies | Requires Playwright |

## Available Indicators

- **CPI Index** (Consumer Price Index, 2010=100)
- **Inflation YoY %** (Year-over-year inflation rate)
- **Food Inflation %** (Food-specific inflation)

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/iran-inflation-data.git
cd iran-inflation-data

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For CBI data (optional)
pip install playwright
playwright install
```

## Usage

### Basic Usage

```bash
python main.py
```

### Output Files

After running the pipeline, you'll find:

- `data/processed/iran_inflation_yearly.csv` - Yearly data
- `data/processed/iran_inflation_monthly.csv` - Monthly data (if available)
- `data/processed/iran_inflation.xlsx` - Excel workbook with multiple sheets
- `data/processed/iran_inflation.sql` - SQL Server script

### Configuration

Edit `src/config.py` to configure:

```python
# SQL Server connection
SQL_SERVER_CONNECTION = "mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server"

# Or set environment variable
export IRAN_INFLATION_DB_URL="mssql+pyodbc://..."
```

## Project Structure

```
iran-inflation-data/
├── src/
│   ├── fetchers/
│   │   ├── world_bank.py    # World Bank API fetcher
│   │   ├── imf.py           # IMF SDMX API fetcher
│   │   └── cbi.py           # Central Bank of Iran scraper
│   ├── processors/
│   │   └── cleaner.py       # Data cleaning & merging
│   ├── exporters/
│   │   ├── csv_exporter.py  # CSV export
│   │   ├── excel_exporter.py # Excel export
│   │   ├── sql_exporter.py  # SQL Server export
│   │   └── sql_script_exporter.py # SQL script generator
│   └── config.py            # Configuration
├── data/
│   ├── raw/                 # Raw fetched data
│   └── processed/           # Cleaned exports
├── main.py                  # Main pipeline entry point
├── requirements.txt         # Python dependencies
└── README.md
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
- See `requirements.txt` for dependencies

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [World Bank API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392)
- [IMF Data Services](https://data.imf.org/)
- [Central Bank of Iran](https://www.cbi.ir/)
