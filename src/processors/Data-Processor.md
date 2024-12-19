# Data Processing Pipeline Documentation

## Purpose
This processor script combines multiple energy market data sources into a single, clean dataset for oil price analysis. It handles these main tasks:

1. Combines data from different sources (prices, production, economic indicators)
2. Converts everything to the same monthly frequency
3. Standardizes column names and formats
4. Handles data validation and quality checks
5. Manages consistent date ranges across all sources

## Input CSV Files (8 files) data/raw
1. wti_YYYYMMDD_HHMMSS.csv (Daily data)
2. currency_YYYYMMDD_HHMMSS.csv (Daily data)
3. inventory_YYYYMMDD_HHMMSS.csv (Weekly data)
4. production_YYYYMMDD_HHMMSS.csv (Monthly data)
5. rigs_YYYYMMDD_HHMMSS.csv (Monthly data)
6. refinery_YYYYMMDD_HHMMSS.csv (Monthly data)
7. gdp_YYYYMMDD_HHMMSS.csv (Quarterly data)
8. inflation_YYYYMMDD_HHMMSS.csv (Annual data)

## Data Processing Pipeline Steps

1. **Initial File Collection & Name Processing**
   ```
   For each data type:
   1. Collect all files in data directory
   2. Find latest file by timestamp in name
   3. Process filename:
      Raw filename with timestamp → Split at first '_' → Extract base name
      Example: wti_20241213_215547.csv → wti.csv
   ```

2. **Data Loading & Initial Clean**
   ```
   For each processed file:
   1. Load CSV data using pandas
   2. Perform basic cleaning:
      - Remove any blank rows
      - Strip whitespace from column names
      - Handle any basic formatting issues
   ```

3. **Column Standardization**
   ```
   Input Columns → Standard Names:
   - wti_timestamp.csv: wti → wti
   - currency_timestamp.csv: currency → eur_usd
   - inventory_timestamp.csv: inventory → inventory
   - production_timestamp.csv: production → production
   - rigs_timestamp.csv: rigs → rigs
   - refinery_timestamp.csv: utilization → refinery_util
   - gdp_timestamp.csv: gdp → gdp
   - inflation_timestamp.csv: inflation → inflation
   ```

4. **Time Series Transformations**
   ```
   Daily Data (wti, eur_usd):
   Daily values → Monthly average → Aligned monthly data

   Weekly Data (inventory):
   Weekly values → Handle missing weeks (resample to daily) → Monthly average → Aligned monthly data

   Monthly Data (production, rigs, refinery):
   Keep as is → Aligned monthly data

   Quarterly Data (gdp):
   Quarterly GDP → forward-fill → Linear interpolation → Monthly values

   Annual Data (inflation):
   Annual rates → forward-fill → Linear interpolation → Monthly values
   ```

   Note: Each transformation includes validation checks and handling of missing/invalid data

5. **Date Standardization**
   ```
   For all datasets:
   1. Convert all dates to datetime
   2. Set all dates to first day of month (YYYY-MM-01)
   3. Verify date format consistency
   ```
6. **Data Validation**
   ```
   1. Check for missing values
   2. Check date frequency
   3. Check for dupicate dates
   4. Check for future dates
   ```

7. **Archive raw files**
   ```
   1. Create archive directory with current data
   2. Move all raw files to archive
   ```

8. **Data Integration**
   ```
   1. Verify all datasets have YYYY-MM-01 formatted dates
   2. Merge all transformed datasets on standardized date column
   3. Ensure no data loss during merge
   4. Date range start from 2005-01-01 (most recent wti starts from 2005-01-01)
   5. Standartize last earliest date by all columns. Truncate rows. 
   6. Verify all columns are present and reorder
   ```

9. **Column Order & Format**
   ```
   Final column order (target variable last):
   1. date
   2. eur_usd
   3. inventory
   4. production
   5. rigs
   6. refinery_util
   7. gdp
   8. inflation
   9. wti          # Target variable placed last
   ```

10. **Save processed file**
   ```
   1. Save processed file in data/processed
   ```


## Output Structure
- Single CSV file containing:
  - Standardized column names as specified
  - All data aligned to monthly frequency
  - Date range: 2005-01-01 onwards
  - No missing values
  - All transformations applied
  - Ready for ML processing

## Output Schema
```
Column Name   | Type      | Description
------------- | --------- | -----------
date          | DATE      | First day of month (YYYY-MM-01)
eur_usd       | FLOAT     | Monthly average EUR/USD exchange rate
inventory     | FLOAT     | Monthly average crude oil inventory levels
production    | FLOAT     | Monthly crude oil production volume
rigs          | INTEGER   | Monthly active oil rigs
refinery_util | FLOAT     | Monthly refinery capacity utilization
gdp           | FLOAT     | Interpolated monthly GDP growth rate
inflation     | FLOAT     | Interpolated monthly inflation rate
wti           | FLOAT     | Monthly average WTI crude oil price (target)
```