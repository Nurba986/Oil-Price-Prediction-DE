# Data Collectors Documentation

## Overview
This package contains a set of data collectors for gathering oil price and related economic data from multiple sources. The collectors are designed to fetch data from EIA (Energy Information Administration) and FRED (Federal Reserve Economic Data) APIs, as well as perform web scraping for additional EIA data.

## Dataflow Diagram
```
EIA API                  FRED API                Web Scraping
  ↓                        ↓                         ↓
- WTI Prices      - EUR/USD Rate         - Oil Production
- Inventory       - GDP                  - Refinery Capacity
                                         - Rig Count 
                                         - Inflation   
  |                        |                         |
  ↓                        ↓                         ↓
       CSV Files with Timestamps (data/raw/)
       - wti_YYYYMMDD.csv 
       - inventory_YYYYMMDD.csv
       - currency_YYYYMMDD.csv
       - inflation_YYYYMMDD.csv
       - gdp_YYYYMMDD.csv
       - production_YYYYMMDD.csv
       - refinery_YYYYMMDD.csv
       - rigs_YYYYMMDD.csv
                   ↓
         Data Processing Pipeline
                   ↓ 
      Standardized CSV Output Files
      (date, value format + validation)
```

## Pipeline Stages

### 1. EIA Data Collector (`collector_eia.py`)
Primary collector for oil and petroleum data from the EIA API.

#### Features:
- Fetches daily WTI (West Texas Intermediate) crude oil prices
- Collects weekly crude oil stocks data
- Uses EIA API v2
- Automatic data saving with timestamps

#### Requirements:
- EIA API key in environment variables as `EIA_API_KEY`
- Valid EIA API subscription

#### Usage:
```python
from collector_eia import EIADataCollector

collector = EIADataCollector()
collector.collect_all()
```

### 2. FRED Collector (`collector_fred.py`)
Collects economic indicators from the Federal Reserve database.

#### Data Points:
- EUR/USD exchange rate (DEXUSEU)
- Inflation rate (FPCPITOTLZGUSA)
- GDP (GDP)

#### Requirements:
- FRED API key in environment variables as `FRED_API_KEY`
- FRED API access

#### Usage:
```python
from collector_fred import FREDCollector

collector = FREDCollector()
collector.collect_all()
```

### 3. EIA Web Scraper (`web_scrap_eia.py`)
Supplementary web scraper for additional EIA data not available through the API.

#### Collected Data:
- U.S. crude oil production
- U.S. refinery capacity
- U.S. drilling rig count

#### Usage:
```python
from web_scrap_eia import EIAWebScraper

scraper = EIAWebScraper()
scraper.collect_all()
```

### 4. Utility Module (`utils.py`)
Shared functionality across all collectors.

#### Features:
- Logging setup
- API error handling
- Standardized CSV file saving with timestamps

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install required packages:
```bash
pip install requests pandas python-dotenv beautifulsoup4
```

3. Set up environment variables:
```bash
# Create .env file
touch .env

# Add API keys to .env
echo "EIA_API_KEY=your_eia_key_here" >> .env
echo "FRED_API_KEY=your_fred_key_here" >> .env
```

## Output Structure
All collectors save data to the `data/raw` directory with the following naming convention:
```
data/raw/
├── wti_YYYYMMDD_HHMMSS.csv         # WTI oil prices
├── inventory_YYYYMMDD_HHMMSS.csv   # Crude oil inventory
├── currency_YYYYMMDD_HHMMSS.csv    # Exchange rates
├── inflation_YYYYMMDD_HHMMSS.csv   # Inflation data
├── gdp_YYYYMMDD_HHMMSS.csv        # GDP data
├── production_YYYYMMDD_HHMMSS.csv  # Oil production
├── refinery_YYYYMMDD_HHMMSS.csv    # Refinery capacity
└── rigs_YYYYMMDD_HHMMSS.csv       # Rig count
```

## Data Format
All collectors output CSV files with a standardized format:
- `date`: Timestamp in YYYY-MM-DD format
- `value`: Numerical value for the respective metric

## Error Handling
- All API calls are wrapped with error handling decorators
- Errors are logged with timestamps and context
- Failed API calls return None instead of crashing
- Data validation before saving to CSV

## Best Practices
1. Always check the `.env` file is properly configured
2. Run collectors during off-peak hours for better performance
3. Monitor the logs for any API failures or data inconsistencies
4. Regularly backup the raw data directory

## Known Limitations
- EIA API has rate limits (check your subscription tier)
- FRED API updates frequency varies by dataset
- Web scraping may break if EIA website structure changes



