"""
A web scraping class for collecting additional oil-related data from EIA's website.
Scrapes data for:
    - U.S. crude oil production
    - U.S. refinery capacity
    - U.S. drilling rig count

Data is collected from EIA's public web pages using BeautifulSoup for HTML parsing.
Each dataset is saved as a separate CSV file with timestamps.
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from utils import setup_logging, api_error_handler, save_to_csv

class EIAWebScraper:
    def __init__(self):
        self.logger = setup_logging(__name__)
        self.urls = {
            'production': 'https://www.eia.gov/dnav/pet/hist/leafhandler.ashx?n=pet&s=mcrfpus2&f=m',
            'refinery': 'https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=MOPUEUS2&f=M',
            'rigs': 'https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=E_ERTRR0_XR0_NUS_C&f=M'
        }

    @api_error_handler
    def fetch_data(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'FloatTitle'})
        
        data = []
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 2:
                year = cols[0].text.strip()
                for month_num, month_col in enumerate(cols[1:], 1):
                    value = month_col.text.strip()
                    if value:
                        try:
                            date = f"{year}-{month_num:02d}-01"
                            value_float = float(value.replace(',', ''))
                            data.append([date, value_float])
                        except ValueError:
                            continue
        
        df = pd.DataFrame(data, columns=['date', 'value'])
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')

    def collect_all(self):
        for name, url in self.urls.items():
            df = self.fetch_data(url)
            save_to_csv(df, name)

if __name__ == '__main__':
    EIAWebScraper().collect_all()