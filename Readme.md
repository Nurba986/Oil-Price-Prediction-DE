# Oil Price Prediction System
A data engineering project that demonstrates end-to-end ETL pipeline development using real-world oil price data.

## Project Overview
This project implements a robust data engineering pipeline for collecting, processing, and analyzing WTI crude oil price data. It showcases best practices in data engineering, including API integration, data validation, error handling, and proper project structure.

## Technical Stack
- **Python** for core implementation
- **Pandas** for data manipulation
- **EIA API** for oil price data
- **Azure Databricks** (planned) for cloud deployment
- **Azure Data Lake Storage** (planned) for data persistence

## Features
- Automated data collection from EIA API
- Daily price tracking and analysis
- Price change calculations
- Proper financial data formatting
- Robust error handling
- Environment variable management
- Production-ready code structure

## Project Structure
```
oil_price_prediction/
├── src/
│   ├── collectors/         # Data collection modules
│   │   └── eia_collector.py
│   ├── processors/        # Data transformation logic
│   └── utils/            # Utility functions
├── tests/                # Unit tests
├── notebooks/           # Analysis notebooks
├── data/               # Data storage
│   ├── raw/           # Raw API data
│   └── processed/     # Transformed data
├── config/            # Configuration files
├── .env              # Environment variables (not in repo)
└── requirements.txt  # Project dependencies
```

## Data Pipeline

### 1. Data Collection
- Automated retrieval from EIA API
- Daily price data extraction
- Initial data validation

### 2. Data Processing
- Price change calculations
- Data cleaning and standardization
- Statistical analysis
- Quality assurance checks

### 3. Data Storage
- Raw data preservation
- Processed data storage
- Historical data management

## Future Enhancements
- Integration with Azure Databricks
- Automated scheduling with Azure Data Factory
- Advanced analytics and ML model development
- Real-time price monitoring
- Interactive dashboards

## Development Practices
- Clean code principles
- Comprehensive error handling
- Environment variable management
- Proper project structure
- Version control best practices

## Contact
- **Developer**: Nurbolat Balginbayev
- **LinkedIn**: [LinkedIn Profile](https://linkedin.com/in/nurbabalgin)

## License
This project is licensed under the MIT License - see the LICENSE file for details.