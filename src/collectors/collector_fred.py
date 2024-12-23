"""
A class for collecting economic data from the Federal Reserve Economic Data (FRED) API.
Fetches important economic indicators:
    - EUR/USD exchange rate (DEXUSEU)
    - GDP (GDP)

Requirements:
    - FRED API key stored in environment variables as 'FRED_API_KEY'
    - requests, pandas, python-dotenv packages
    - utils.py for helper functions
"""

import os
import pandas as pd
import requests
from dotenv import load_dotenv
from utils import setup_logging, api_error_handler, save_to_csv

class FREDCollector:
    def __init__(self):
        self.logger = setup_logging(__name__)
        load_dotenv()
        self.api_key = os.getenv('FRED_API_KEY')
        if not self.api_key:
            raise ValueError("FRED API key not found")
        
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
        self.series = {
            'currency': 'DEXUSEU',         
            'gdp': 'GDP'
        }

    @api_error_handler
    def fetch_data(self, series_id):
        response = requests.get(
            self.base_url,
            params={'series_id': series_id, 'api_key': self.api_key, 'file_type': 'json'}
        ).json()
        
        df = pd.DataFrame(response['observations'])
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        return df[['date', 'value']].dropna()

    def collect_all(self):
        for name, series_id in self.series.items():
            df = self.fetch_data(series_id)
            save_to_csv(df, name)

if __name__ == "__main__":
    FREDCollector().collect_all()