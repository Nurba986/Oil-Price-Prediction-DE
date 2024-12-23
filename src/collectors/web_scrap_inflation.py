"""
Web scraper for collecting US inflation rate data from usinflationcalculator.com.
Saves data in CSV format with timestamps in the data/raw directory.
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os
from utils import setup_logging, api_error_handler, save_to_csv

class USInflationScraper:
    def __init__(self):
        self.logger = setup_logging(__name__)
        self.url = 'https://www.usinflationcalculator.com/inflation/current-inflation-rates/'
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    @api_error_handler
    def fetch_data(self):
        """Fetch and parse inflation data from the website."""
        response = requests.get(self.url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')  # The inflation rate table
        
        if not table:
            raise ValueError("Could not find inflation rate table on webpage")
            
        return table

    def parse_table(self, table):
        """Parse the HTML table and extract inflation rates."""
        data = []
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            cols = row.find_all('td')
            if not cols:
                continue
                
            year = cols[0].text.strip()
            
            # Process each month's data
            for month_idx, col in enumerate(cols[1:13]):  # Skip year and Ave columns
                value = col.text.strip()
                
                # Skip if value contains 'avail' or is empty
                if 'Avail.' in value.lower() or not value:
                    continue
                    
                try:
                    # Convert value to float and create date
                    rate = float(value)
                    date = f"{year}-{month_idx+1:02d}-01"
                    data.append([date, rate])
                except ValueError:
                    self.logger.warning(f"Could not parse value: {value} for {year}-{self.months[month_idx]}")
                    continue
        
        return pd.DataFrame(data, columns=['date', 'value'])

    def collect_data(self):
        """Main method to collect and save inflation data."""
        try:
            # Fetch and parse data
            table = self.fetch_data()
            df = self.parse_table(table)
            
            # Sort by date
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Save data using utility function
            save_to_csv(df, 'inflation')
            
            self.logger.info(f"Successfully collected {len(df)} inflation records")
            return df
            
        except Exception as e:
            self.logger.error(f"Error collecting inflation data: {str(e)}")
            raise

if __name__ == "__main__":
    scraper = USInflationScraper()
    scraper.collect_data()