"""
Utility functions for data collection and processing.
Provides common functionality used across different collectors:
    - Logging setup
    - API error handling
    - CSV file saving with timestamps

The functions handle common tasks like:
    - Setting up consistent logging across all collectors
    - Gracefully handling and logging API errors
    - Saving data with standardized naming and timestamps
"""

import logging
from datetime import datetime
from functools import wraps
import pandas as pd
import os

# Logging set up (basic info level)
def setup_logging(name):
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)

# Decorator for API error handling (logs errors and returns none)
def api_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            return None
    return wrapper

# Saves DataFrame to CSV with timestamp and logging
def save_to_csv(df, prefix):
    if df is not None and not df.empty:
        timestamp = datetime.now().strftime('%Y%m%d')
        path = f"data/raw/{prefix}_{timestamp}.csv"
        os.makedirs("data/raw", exist_ok=True) # Directory path
        df.to_csv(path, index=False)
        logging.info(f"Saved {prefix} data: {len(df)} records")