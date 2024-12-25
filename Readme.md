# Oil Price Prediction System
A data engineering pipeline for oil price analysis and prediction using WTI crude oil data.

## Overview
End-to-end data engineering solution that collects, processes, and analyzes oil price data, orchestrates and ML modeling.

Note: "For a visual overview of the data pipeline and processing stages, see flowchart.md"

## Key Components

### Data Collection
- EIA API integration for oil prices and inventory data
- FRED API for economic indicators
- Web scraping for supplementary data

### Data Processing
- Standardization and cleaning
- Frequency conversion (daily/weekly/quarterly to monthly)
- Feature engineering and selection
- Quality validation and archiving

### Machine Learning
- XGBoost model for price prediction
- Time series cross-validation
- Directional accuracy focus
- Confidence-based predictions

### Orchestration
- Automated pipeline execution every Thursday at 5 PM Chicago time
- Three-stage pipeline execution:
    - Data Collection: EIA and FRED APIs, web scraping
    - Data Processing: Raw data processing and feature engineering
    - Forecasting: Price predictions and email notifications with forecast

## Project Structure
```
├── data/              # Data storage
├── notebook/          # Jupyter notebooks
└── src/               # Source code
    ├── collectors/    # API collectors
    ├── processors/    # Data processors
    └── forecasting/   # ML pipeline

```

## Requirements
- Python 3.8+
- EIA and FRED API keys
- Environment variables in .env file

## Contact
Developer: Nurbolat Balginbayev  
LinkedIn: [LinkedIn Profile](https://linkedin.com/in/nurbabalgin)

## License
MIT License