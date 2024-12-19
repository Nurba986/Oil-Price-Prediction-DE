# Oil Price Prediction System
A data engineering pipeline for oil price analysis and prediction using WTI crude oil data.

## Overview
This project implements an end-to-end data engineering solution that collects, processes, and analyzes oil price data, featuring API integration, ML modeling, and cloud deployment capabilities.

## Getting Started
### Prerequisites
- Python 3.8+
- EIA API key
- FRED API key
- Azure account (for cloud deployment)
- Apache Airflow

### Installation
1. Clone the repository
```bash
git clone https://github.com/yourusername/oil-price-prediction.git
cd oil-price-prediction
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your API keys and configurations
```

## Project Phases

### Phase 1: Data Collection & Storage
#### 1. API Integration
- Get EIA and FRED API keys
  - Register at EIA website
  - Set up FRED developer account
- Create FRED data collector
  - Implement historical data fetch
  - Set up incremental updates
- Create EIA data collector
  - Configure API endpoints
  - Implement rate limiting
- Create EIA scrapper
- Test collectors with CSV output in data/raw
  - Validate data completeness
  - Check API response handling

#### 2. Data Processing
- Standardize column names and formats
  - Define naming conventions
  - Implement data type validation
- Convert data frequencies
  - Daily to monthly aggregation
  - Handle different time zones
- Validate data quality (initial_exploration)
  - Identify outliers
  - Handle missing values
  - Ensure date consistency
- Archive and process data
  - Raw data backup
  - Generate clean datasets

#### 3. Exploratory Data Analysis
- Statistical analysis
- Correlation studies
- Time series visualization
- Seasonal pattern analysis

#### 4. Feature Data Processing
- Feature engineering
- Data transformation
- Feature selection analysis

### Phase 2: Machine Learning
#### 1. Machine Learning Pipeline
- Feature selection implementation
  - Correlation analysis
  - Feature importance ranking
- Training pipeline setup
  - Data splitting strategy
  - Cross-validation setup
- Model evaluation framework
  - Metrics definition
  - Validation procedures
- Prediction dashboard
  - Interactive visualizations
  - Real-time updates
- Accuracy monitoring
  - Performance tracking
  - Model retraining triggers

### Phase 3: Orchestration and Cloud Migration
#### 1. Orchestration Pipeline
- Apache Airflow setup
  - DAG configuration
  - Task dependencies
  - Error handling
  - Scheduling optimization

#### 2. Core Monitoring
- Alert system implementation
  - Data freshness monitoring
  - Pipeline failure detection
  - Model drift tracking
  - Resource utilization
  - Security monitoring

#### 3. Cloud Migration
- Databricks implementation
  - Cluster configuration
  - Performance optimization
- Data Lake setup
  - Storage organization
  - Access controls
- Security implementation
  - Authentication
  - Encryption
  - Compliance checks
- Pipeline migration
  - Testing procedures
  - Rollback plans

## Project Structure
```
├── data/
│   ├── archive/         # Archived raw data
│   ├── processed/       # Cleaned and processed datasets
│   └── raw/            # Raw data from APIs
├── notebook/
│   ├── data_initial_expl.ipynb  # Initial data exploration
│   └── docs.md                  # Documentation
├── src/
│   ├── collectors/     # API data collection scripts
│   └── processor/      # Data processing modules
├── venv/              # Virtual environment
├── .env               # Environment variables
├── .gitignore         # Git ignore rules
└── README.md          # Project documentation
```

## Future Enhancements
- Real-time price prediction updates
- Advanced feature engineering
- Integration with additional data sources
- Enhanced visualization dashboard
- Automated model retraining
- Mobile app development

## Contact
Developer: Nurbolat Balginbayev
LinkedIn: [LinkedIn Profile](https://linkedin.com/in/nurbabalgin)

## License
MIT License