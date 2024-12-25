# Model Validation Pipeline

## Purpose
Validates WTI oil price prediction model and generates performance metrics.

## Core Steps

### 1. Data Preparation
- Loads latest training data
- Features: EUR/USD, inventory, production, rigs, inflation, WTI rolling averages
- Splits: 80% training, 20% testing

### 2. Model Validation
- Loads latest model
- Calculates key metrics:
  - RMSE (Root Mean Square Error)
  - MAE (Mean Absolute Error)
  - MAPE (Mean Absolute Percentage Error)
  - DA (Directional Accuracy)

### 3. Output Generation
- Saves metrics to `results/metrics_YYYYMMDD.txt`
- Creates plots in `results/plots/`:
  - Training predictions
  - Test predictions

## Key Checks
1. Check training.log for errors
2. Review metrics file
3. Inspect prediction plots