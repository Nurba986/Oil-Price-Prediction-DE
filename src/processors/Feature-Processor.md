# Feature Processing Pipeline Documentation

## Purpose
Transform processed data into ML-ready format by removing low-correlation features and adding time-series derived features optimized for WTI price prediction modeling.

## Input 
1. Source: `data/processed/processed_data_YYYYMMDD.csv`
2. Format: CSV file with monthly frequency
3. Required Columns:
   - date: YYYY-MM-DD
   - eur_usd: float
   - inventory: float
   - production: float
   - rigs: float
   - refinery_util: float (to be dropped)
   - gdp: float (to be dropped)
   - inflation: float
   - wti: float

## Feature Processing Pipeline Steps

1. Data Validation
   - Verify all required columns exist
   - Check data types
   - Confirm monthly frequency
   - Verify no missing values in input data

2. Feature Removal
   - Drop gdp column (correlation: -0.12)
   - Drop refinery_utilization column (correlation: 0.10)

3. Feature Engineering
   - Add 6-month WTI rolling mean (strong correlation: 0.89)
   - Add 12-month WTI rolling mean (moderate correlation: 0.75)
   - Add 6-month WTI price lag (correlation: 0.57)

4. Handle Rolling Window Data
   - Initial rows will have NaN values from rolling calculations
   - Drop first 12 months of data (ensures all rolling means are calculated)
   - Verify no remaining NaN values after drop
   - Reset index after dropping rows

5. Quality Checks
   - Verify no missing values in final dataset
   - Confirm expected data ranges
   - Validate engineered feature calculations
   - Check date continuity after row removal

6. Export
   - Save to `data/training_ready/training_ready_data_YYYYMMDD.csv`

Data Flow:
```
processed_data.csv -> feature_processor.py -> [drop first 6 months] -> training_ready_data.csv
```

## Output Structure

Final Columns:
1. date (YYYY-MM-DD)
2. eur_usd (float)
3. inventory (float)
4. production (float)
5. rigs (float)
6. inflation (float)
7. wti_6m_rolling (float)
8. wti_12m_rolling (float)
9. wti_6m_lag (float)
10. wti (float, target variable)

## Output Schema

1. File Location: `data/training_ready/training_ready_data_YYYYMMDD.csv`

2. Data Characteristics:
   - Frequency: Monthly
   - Date Range: 2006-2022 (first 12 months removed)
   - No missing values
   - All features numeric except date

3. File Naming Convention:
   - file: training_ready_data_YYYYMMDD.csv


