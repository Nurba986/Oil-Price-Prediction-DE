import os
import requests
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path

class EIADataCollector:
    def __init__(self):
        # Find the root directory (where .env is located)
        root_dir = Path(__file__).resolve().parents[2]  # Go up 2 levels from collectors/eia_collector.py
        dotenv_path = root_dir / '.env'
        
        # Load environment variables from the correct path
        load_dotenv(dotenv_path)
        
        # Get API key
        self.api_key = os.getenv('EIA_API_KEY')
        if not self.api_key:
            raise ValueError("EIA API key not found in environment variables")
        
    def get_oil_prices(self, days_back=30):
        """Get WTI crude oil prices for the specified number of days"""
        
        # Setup API request
        url = "https://api.eia.gov/v2/petroleum/pri/spt/data"
        params = {
            'api_key': self.api_key,
            'frequency': 'daily',
            'data[]': 'value',
            'facets[series][]': 'RWTC',
            'length': days_back,
            'sort[0][column]': 'period',
            'sort[0][direction]': 'desc'
        }
        
        try:
            # Make request
            print("Fetching oil price data...")
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise exception for bad status codes
            
            # Parse response
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data['response']['data'])
            
            # Process DataFrame
            if not df.empty:
                df['period'] = pd.to_datetime(df['period'])
                df = df.rename(columns={'value': 'price'})
                df = df[['period', 'price']]
                df['price'] = pd.to_numeric(df['price'])
                df = df.sort_values('period', ascending=False)
                
                # Calculate daily price changes
                df['price_change'] = df['price'].diff(-1)  # Negative diff because we're sorted descending
                df['price_change_pct'] = (df['price_change'] / df['price'].shift(-1) * 100)
                
                return df
            else:
                print("No data found")
                return None
                
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return None

def main():
    # Create collector
    collector = EIADataCollector()
    
    # Get last 30 days of prices
    df = collector.get_oil_prices(30)
    
    if df is not None:
        print("\nLatest WTI Crude Oil Prices:")
        print("\nSummary Statistics:")
        print(f"Current Price: ${df['price'].iloc[0]:.2f}")
        print(f"30-Day High: ${df['price'].max():.2f}")
        print(f"30-Day Low: ${df['price'].min():.2f}")
        print(f"30-Day Average: ${df['price'].mean():.2f}")
        
        print("\nDaily Prices (Last 10 days):")
        pd.set_option('display.float_format', '${:,.2f}'.format)
        print(df.head(10).to_string(index=False))
        
        # Calculate some basic statistics
        print("\nPrice Changes:")
        latest_change = df['price_change'].iloc[0]
        latest_change_pct = df['price_change_pct'].iloc[0]
        print(f"Latest Daily Change: ${latest_change:.2f} ({latest_change_pct:.1f}%)")

if __name__ == "__main__":
    main()