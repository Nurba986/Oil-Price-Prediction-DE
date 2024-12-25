# Pipeline Orchestrator

Automated data pipeline scheduler that coordinates data collection, processing, and forecasting tasks.

## Data Flow Diagram
```
Scheduled Pipeline (Every Thursday 5PM Chicago)
------------------------------------------
Data Collection (Stage 1)           Error Handling
    EIA, FRED & Web Scraping  -->  Logging & Validation
           ↓
Data Processing (Stage 2) 
    Processing & Feature Eng
           ↓ 
Forecasting (Stage 3)
    |                      |
WTIForecaster     NotificationHandler
    ↓                      ↓
Generate Forecast    Load Forecast
    ↓                      ↓
Save JSON File      Create Visualization
    ↓                      ↓
  Complete         Send Email Notification
```

## Key Features

- Runs every Thursday at 5 PM Chicago time
- Three-stage pipeline execution:
  1. Data Collection (EIA, FRED, web scraping)
  2. Data Processing
  3. Forecasting and Notifications

## Setup

1. Project requires `.env` file in root directory
2. Creates `logs` directory automatically
3. Logs pipeline execution to both file and stdout

## Usage

```bash
python pipeline_orchestrator.py
```

First run executes pipeline immediately for testing, then switches to scheduled mode.

## Error Handling

- Comprehensive logging of all operations
- Fails fast if any pipeline stage encounters errors
- Maintains execution context through project root detection

## Dependencies

- schedule
- pytz
- logging
- subprocess
- pathlib

## Project Structure

```
project_root/
├── src/
│   ├── collectors/
│   ├── processors/
│   └── forecasting/
└── logs/
```