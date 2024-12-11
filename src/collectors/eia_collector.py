import os
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv

class OilPriceCollector:
    def __init__(self):
        # Load API key from .env file
        env_path = Path(__file__).resolve().parents[2] / '.env'
        load_dotenv(env_path)
        
        self.api_key = os.getenv('EIA_API_KEY')
        if not self.api_key:
            raise ValueError("EIA API key not found")
    
    def get_prices(self, days=30):
        """Fetch WTI crude oil prices from EIA API"""
        url = "https://api.eia.gov/v2/petroleum/pri/spt/data"
        params = {
            'api_key': self.api_key,
            'frequency': 'daily',
            'data[]': 'value',
            'facets[series][]': 'RWTC',  # WTI Crude Oil series
            'length': days,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Convert response to DataFrame
            df = pd.DataFrame(response.json()['response']['data'])
            
            if df.empty:
                print("No data found")
                return None
            
            # Process the data
            df['period'] = pd.to_datetime(df['period'])
            df = df.rename(columns={'value': 'price'})
            df = df[['period', 'price']]
            df['price'] = pd.to_numeric(df['price'])
            
            # Calculate price changes
            df['price_change'] = df['price'].diff(-1)
            df['price_change_pct'] = (df['price_change'] / df['price'].shift(-1) * 100)
            
            return df
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

def main():
    collector = OilPriceCollector()
    df = collector.get_prices(30)
    
    if df is not None:
        # Display summary
        print("\nWTI Crude Oil Summary:")
        print(f"Current Price: ${df['price'].iloc[0]:.2f}")
        print(f"30-Day High: ${df['price'].max():.2f}")
        print(f"30-Day Low: ${df['price'].min():.2f}")
        print(f"30-Day Average: ${df['price'].mean():.2f}")
        print(f"Latest Daily Change: ${df['price_change'].iloc[0]:.2f} ({df['price_change_pct'].iloc[0]:.1f}%)")

if __name__ == "__main__":
    main()