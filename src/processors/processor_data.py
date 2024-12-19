import pandas as pd
import numpy as np
from pathlib import Path
import re
from datetime import datetime
import logging
import os
import shutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, raw_data_dir='data/raw', output_dir='data/processed'):
        """Initialize the data processor with directory paths."""
        self.raw_data_dir = Path(raw_data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Add archive directory path within raw data directory
        self.archive_dir = self.raw_data_dir / 'archive'
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Define expected column mappings
        self.column_mapping = {
            'wti': 'wti',
            'currency': 'eur_usd',
            'inventory': 'inventory',
            'production': 'production',
            'rigs': 'rigs',
            'refinery': 'refinery_util',
            'gdp': 'gdp',
            'inflation': 'inflation'
        }
        
        # Define expected frequencies
        self.frequencies = {
            'wti': 'D',        # Daily
            'currency': 'D',   # Daily
            'inventory': 'W',  # Weekly
            'production': 'M', # Monthly
            'rigs': 'M',      # Monthly
            'refinery': 'M',  # Monthly
            'gdp': 'Q',       # Quarterly
            'inflation': 'A'   # Annual
        }

    def get_latest_file(self, base_name):
        """Find the latest file for a given base name using timestamp in filename."""
        pattern = f"{base_name}_\\d{{8}}_\\d{{6}}\\.csv$"
        matching_files = [f for f in self.raw_data_dir.glob(f"{base_name}_*.csv") 
                         if re.match(pattern, f.name)]
        
        if not matching_files:
            raise FileNotFoundError(f"No matching files found for {base_name}")
            
        latest_file = max(matching_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"Found latest file for {base_name}: {latest_file.name}")
        return latest_file

    def load_and_clean_data(self, file_path, base_name):
        """Load CSV data and perform initial cleaning."""
        try:
            df = pd.read_csv(file_path)
            
            # Basic cleaning
            df.columns = df.columns.str.strip().str.lower()
            df = df.dropna(how='all')
            
            # Ensure date column exists and is properly formatted
            date_col = [col for col in df.columns if 'date' in col.lower()][0]
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.rename(columns={date_col: 'date'})
            
            # Rename target column according to mapping
            value_col = [col for col in df.columns if col != 'date'][0]
            df = df.rename(columns={value_col: self.column_mapping[base_name]})
            
            logger.info(f"Successfully loaded and cleaned {base_name} data")
            return df
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise

    def standardize_to_monthly(self, df, base_name):
        """Convert data to monthly frequency with proper handling based on original frequency."""
        freq = self.frequencies[base_name]
        
        # Set date as index
        df = df.set_index('date')
        
        if freq == 'D':  # Daily to Monthly
            df = df.resample('M').mean()
            
        elif freq == 'W':  # Weekly to Monthly
            # First resample to daily to handle missing weeks
            df = df.resample('D').interpolate(method='linear')
            # Then resample to monthly
            df = df.resample('M').mean()
            
        elif freq == 'Q':  # Quarterly to Monthly
            # Interpolate to monthly
            df = df.resample('M').ffill().interpolate(method='linear')
            
            
        elif freq == 'A':  # Annual to Monthly
            df = df.resample('M').ffill().interpolate(method='linear')
            
        # Reset index and ensure date is first of month
        df = df.reset_index()
        df['date'] = df['date'].dt.to_period('M').dt.to_timestamp()
        
        logger.info(f"Standardized {base_name} data to monthly frequency")
        return df

    def validate_data(self, df):
        """Perform validation checks on the final dataset."""
        # Check for missing values
        if df.isnull().any().any():
            raise ValueError("Dataset contains missing values")
            
        # Check date frequency
        date_diff = df['date'].diff().dropna()
        if not all(date_diff.dt.days.between(28, 31)):
            raise ValueError("Inconsistent monthly frequency detected")
            
        # Check for duplicate dates
        if df['date'].duplicated().any():
            raise ValueError("Duplicate dates found in dataset")
            
        # Check for future dates
        if (df['date'] > pd.Timestamp.now()).any():
            raise ValueError("Future dates found in dataset")
            
        logger.info("Data validation passed successfully")
        return True

    def archive_raw_files(self):
        """Archive raw data files to dated archive folder"""
        try:
            # Create archive directory with current data
            current_date = datetime.now().strftime('%Y-%m-%d')
            date_archive_dir = self.archive_dir / current_date
            date_archive_dir.mkdir(parents=True, exist_ok=True)

            # Move each raw file to archive
            for base_name in self.column_mapping.keys():
                try:
                    raw_file = self.get_latest_file(base_name)
                    archive_path = date_archive_dir / raw_file.name
                    shutil.move(str(raw_file), str(archive_path))
                    logger.info(f"Archived {raw_file.name} to {archive_path}")
                except Exception as e:
                    logger.error(f"Error archiving {base_name} file: {str(e)}")
                    raise

            logger.info(f"Succesfully archived all raw files to {date_archive_dir}")

        except Exception as e:
            logger.error(f"Error in archiving process: {str(e)}")
            raise

    def process_data(self):
        """Main processing pipeline."""
        try:
            all_data = []
            
            # Process each data type
            for base_name in self.column_mapping.keys():
                # Get latest file
                latest_file = self.get_latest_file(base_name)
                
                # Load and clean data
                df = self.load_and_clean_data(latest_file, base_name)
                
                # Convert to monthly frequency
                df = self.standardize_to_monthly(df, base_name)
                
                all_data.append(df)
            
            # Merge all datasets
            final_df = all_data[0]
            for df in all_data[1:]:
                final_df = pd.merge(final_df, df, on='date', how='outer')
                
            # Filter date range to start from 2005-01-01
            final_df = final_df[final_df['date'] >= '2005-01-01']
            
            # Find the earliest last date among all columns
            last_dates = {}
            for column in final_df.columns:
                if column != 'date':
                    valid_dates = final_df[~final_df[column].isna()]['date']
                    if len(valid_dates) > 0:
                        last_dates[column] = valid_dates.max()
            
            earliest_last_date = min(last_dates.values())
            logger.info(f"Truncating all data to {earliest_last_date}")
            
            # Truncate all data to the earliest last date
            final_df = final_df[final_df['date'] <= earliest_last_date]
            
            # Reorder columns
            column_order = ['date', 'eur_usd', 'inventory', 'production', 'rigs',
                        'refinery_util', 'gdp', 'inflation', 'wti']
            final_df = final_df[column_order]
            
            # Validate final dataset
            self.validate_data(final_df)
            
            # Save processed data with timestamp
            timestamp = datetime.now().strftime('%Y%m%d')
            output_file = self.output_dir / f'processed_data_{timestamp}.csv'
            final_df.to_csv(output_file, index=False)
            logger.info(f"Successfully saved processed data to {output_file}")
            
            # Archive raw files after successful processing
            self.archive_raw_files()

            return final_df
            
        except Exception as e:
            logger.error(f"Error in processing pipeline: {str(e)}")
            raise
            
if __name__ == "__main__":
    try:
        processor = DataProcessor()
        processed_data = processor.process_data()
        logger.info("Data processing completed successfully")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise