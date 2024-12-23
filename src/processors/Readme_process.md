# Data and Feature Processing Pipeline Documentation

## Overview
This documentation covers the end-to-end data processing pipeline for oil price analysis, from raw data integration through feature engineering for machine learning readiness.

## Pipeline Stages

### Stage 1: Data Processing
Combines multiple energy market data sources into a single, clean dataset.

#### Input Data Sources
Raw data files located in `data/raw/`:

1. **Daily Frequency**
   - WTI crude oil prices (`wti_YYYYMMDD.csv`)
   - Currency exchange rates (`currency_YYYYMMDD.csv`)

2. **Weekly Frequency**
   - Oil inventory levels (`inventory_YYYYMMDD.csv`)

3. **Monthly Frequency**
   - Oil production (`production_YYYYMMDD.csv`)
   - Rig count (`rigs_YYYYMMDD.csv`)
   - Refinery utilization (`refinery_YYYYMMDD.csv`)
   - Inflation (`inflation_YYYYMMDD.csv`)

4. **Other Frequencies**
   - GDP (Quarterly) (`gdp_YYYYMMDD.csv`)


#### Processing Steps

1. **File Processing**
   - Collect latest files by timestamp
   - Standardize file naming
   - Basic data cleaning

2. **Column Standardization**
   ```
   Raw Column → Standardized Name
   - wti → wti
   - currency → eur_usd
   - inventory → inventory
   - production → production
   - rigs → rigs
   - utilization → refinery_util
   - gdp → gdp
   - inflation → inflation
   ```

3. **Time Series Transformations**
   - Daily data → Monthly average
   - Weekly data → Fill gaps → Monthly average
   - Quarterly GDP → Linear interpolation → Monthly
   - Annual inflation → Linear interpolation → Monthly

4. **Data Validation**
   - Missing value checks
   - Frequency validation
   - Duplicate detection
   - Future date checks

5. **Data Integration**
   - Merge all datasets on standardized dates
   - Verify data completeness
   - Standard date range (2005-01-01 onwards)
   - Column reordering

#### Stage 1 Output
File: `data/processed/processed_data_YYYYMMDD.csv`

```
Column Name   | Type      | Description
------------- | --------- | -----------
date          | DATE      | YYYY-MM-01 format
eur_usd       | FLOAT     | Exchange rate
inventory     | FLOAT     | Oil inventory
production    | FLOAT     | Oil production
rigs          | INTEGER   | Active rigs
refinery_util | FLOAT     | Refinery usage
gdp           | FLOAT     | Monthly GDP
inflation     | FLOAT     | Monthly inflation
wti           | FLOAT     | Target variable
```

### Stage 2: Feature Processing
Transforms processed data into ML-ready format with engineered features.

#### Input
- Source: `data/processed/processed_data_YYYYMMDD.csv`
- Frequency: Monthly
- Date Format: YYYY-MM-DD

#### Processing Steps

1. **Data Validation**
   - Column presence verification
   - Data type checking
   - Frequency confirmation
   - Missing value detection

2. **Feature Selection**
   - Remove low-correlation features:
     - GDP (correlation: -0.12)
     - Refinery utilization (correlation: 0.10)

3. **Feature Engineering**
   - Add WTI-based features:
     - 6-month rolling mean (correlation: 0.89)
     - 12-month rolling mean (correlation: 0.75)
     - 6-month lag (correlation: 0.57)

4. **Data Preparation**
   - Remove initial 12 months (rolling window requirement)
   - Validate calculations
   - Reset index

5. **Quality Assurance**
   - Range validation
   - Engineered feature verification
   - Date continuity checks

#### Stage 2 Output
File: `data/training_ready/training_ready_data_YYYYMMDD.csv`

Final Column Structure:
1. date (YYYY-MM-DD)
2. eur_usd (float)
3. inventory (float)
4. production (float)
5. rigs (float)
6. inflation (float)
7. wti_6m_rolling (float)
8. wti_12m_rolling (float)
9. wti_6m_lag (float)
10. wti (float, target)

## Data Flow Diagram
```
Raw Data (8 files)
      ↓
Data Processing
      ↓
Processed Data (9 columns)
      ↓
Feature Engineering
      ↓
Training Ready Data (10 columns)
```

## Usage Notes

1. **File Management**
   - Raw files are automatically archived after processing
   - Processed files maintain date stamps in names
   - Each stage validates input before processing

2. **Data Validation**
   - Both stages include comprehensive validation
   - Processing stops if validation fails
   - All transformations are logged

3. **Best Practices**
   - Monitor logs for transformation issues
   - Verify date ranges after processing
   - Check correlation values periodically
   - Backup data before major transformations

4. **Known Limitations**
   - Requires 12 months of historical data
   - Some features removed due to low correlation
   - Linear interpolation for economic indicators