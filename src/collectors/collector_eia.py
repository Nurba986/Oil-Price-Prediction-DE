"""
A class for collecting oil and petroleum data from the U.S. Energy Information Administration (EIA) API.
This collector fetches daily WTI (West Texas Intermediate) crude oil prices and weekly crude oil stocks data.

Requirements:
    - EIA API key stored in environment variables as 'EIA_API_KEY'
    - requests, pandas, python-dotenv packages
    - utils.py for helper functions
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv
from utils import setup_logging, api_error_handler, save_to_csv

class EIADataCollector:
    def __init__(self): 
        self.logger = setup_logging(__name__) 
        load_dotenv() 
        self.api_key = os.getenv('EIA_API_KEY')
        if not self.api_key:
            raise ValueError("EIA API key not found") 
        
        self.base_url = "https://api.eia.gov/v2" 

    @api_error_handler 
    def fetch_data(self, endpoint, params): 
        params['api_key'] = self.api_key
        response = requests.get(f"{self.base_url}/{endpoint}", params=params) 
        response.raise_for_status()
        return response.json()['response']['data']

    def get_data(self, endpoint, params, value_column):
        data = self.fetch_data(endpoint, params)
        if data:
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['period'])
            return df[['date', 'value']].rename(columns={'value': value_column})
        return None

    def collect_all(self):
        # WTI Prices
        wti_params = {
            'frequency': 'daily',
            'data[]': 'value',
            'facets[series][]': 'RWTC',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': 5000
        }
        wti_df = self.get_data('petroleum/pri/spt/data', wti_params, 'value')
        save_to_csv(wti_df, 'wti')

        # Crude Stocks
        stocks_params = {
            'frequency': 'weekly',
            'data[]': 'value',
            'facets[series][]': 'WCESTUS1',
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc',
            'length': 5000
        }
        stocks_df = self.get_data('petroleum/stoc/wstk/data', stocks_params, 'value')
        save_to_csv(stocks_df, 'inventory')

if __name__ == "__main__":
    EIADataCollector().collect_all()