# WTI Price Forecasting System

This system provides functionality for generating WTI oil price forecasts and sending automated notifications.

## Data Flow Diagram
   ```
    WTIForecaster              NotificationHandler
         ↓                             ↓
  Generate Forecast               Load Forecast
         ↓                             ↓
    Save JSON File             Create Visualization
         ↓                             ↓
      Complete                Send Email Notification
   ```
## Detailed Data Flow Diagram
1. Model Forecasting Process:
```
   Load Latest Model & Scaler
             ↓
      Load Training Data
             ↓
       Prepare Features
             ↓
     Generate Predictions
             ↓
 Calculate Confidence Intervals
             ↓
     Save Forecast JSON
```

2. Notification Process:
```
     Load Latest Forecast
             ↓
   Create Visualization Plot
             ↓
   Generate HTML Email Content
             ↓
     Attach Plot to Email
             ↓
     Send Notification
```

## Components

### 1. Model Forecaster (`model_forecast.py`)

Generates 3-month WTI price forecasts using trained ML models.

Key Features:
- Loads latest trained model and scaler
- Generates forecasts for next 3 months
- Provides confidence intervals for predictions
- Applies confidence decay for longer-term predictions
- Saves forecasts in JSON format

Usage:
```python
from model_forecast import WTIForecaster
forecaster = WTIForecaster()
forecasts = forecaster.generate_forecast()
```

### 2. Notification Handler (`notification_handler.py`)

Sends email notifications with forecast results and visualizations.

Key Features:
- Creates visualization plots of forecasts
- Generates formatted HTML email content
- Sends emails with attached forecast plots
- Handles SMTP email configuration and sending
- Includes error handling and logging

Usage:
```python
from notification_handler import NotificationHandler
handler = NotificationHandler()
handler.send_notification()
```

## Requirements
- Environment variables:
  - `SENDER_EMAIL`: Email address for sending notifications
  - `SENDER_PASSWORD`: Email password/app token
  - `RECIPIENT_EMAIL`: Recipient email address

## Output Format
Forecast JSON structure:
```json
{
    "current_wti": float,
    "forecasts": [
        {
            "forecast_date": "YYYY-MM-DD",
            "predicted_price": float,
            "confidence_interval": {
                "lower": float,
                "upper": float
            },
            "confidence": float
        }
    ]
}
```