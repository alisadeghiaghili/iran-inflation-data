"""Configuration for the Iran inflation data pipeline."""
import os

# SQL Server connection (fill in your credentials)
SQL_SERVER_CONNECTION = os.environ.get(
    "IRAN_INFLATION_DB_URL",
    "mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server"
)

# Output directories
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")

# API settings
API_RETRY_ATTEMPTS = 2
API_RETRY_DELAY = 1  # seconds between retries
REQUEST_TIMEOUT = 10  # seconds (connect timeout, read timeout)

# CBI scraping settings
CBI_SCRAPING_DELAY = 0.5  # seconds between requests

# World Bank API base URL
WORLD_BANK_API_BASE = "https://api.worldbank.org/v2"

# World Bank indicators for Iran
WORLD_BANK_INDICATORS = {
    "FP.CPI.TOTL": "Consumer Price Index (2010=100)",
    "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)",
    "FP.CPI.TOTL.FD.ZG": "Food inflation (consumer prices, annual %)",
}

# IMF SDMX API
IMF_SDMX_BASE = "https://dataservices.imf.org/REST/SDMX_JSON.svc"

# CBI website
CBI_BASE_URL = "https://www.cbi.ir"
