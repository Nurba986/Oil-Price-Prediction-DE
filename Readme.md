# Oil Price Prediction System
A data engineering pipeline for oil price analysis and prediction using WTI crude oil data.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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
├── data/
│   └── training_ready/          # Directory for processed training data
│
├── models/                      # Directory for model files and artifacts
│   ├── trained_models/          # Trained model weights and parameters
│   ├── model_configs/
│   └── scalers/           
│
├── notebook/                    # Jupyter notebooks for experimentation and analysis
│   ├── init_exploration.ipynb
│   ├── eda_analysis.ipynb
│   └── model_training.ipynb
│
├── results/                     # Directory for storing model results and evaluations
│   ├── forecasts/
│   ├── metrics/
│   └── plots/
│
├── src/                         # Source code directory
│   ├── collectors/                   
│   ├── forecasting/
│   ├── model_validation/
│   ├── orchestration 
│   │
│
├── .gitignore                 # Git ignore file
├── Flowcharts.md              # System flowcharts documentation
├── README.md                  # Project documentation and setup instructions
├── requirements.txt           # Project dependencies
└── LICENSE                    # MIT License file
```

## Requirements
- Python 3.8+
- EIA and FRED API keys
- Environment variables in .env file

## Contact
Developer: Nurbolat Balginbayev  
LinkedIn: [LinkedIn Profile](https://linkedin.com/in/nurbabalgin)


