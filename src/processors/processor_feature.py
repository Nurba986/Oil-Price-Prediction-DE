import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeatureProcessor:
    def __init__(self, data_dir="data/processed"):
        """Initialize FeatureProcessor."""

        self.input_path = self.get_latest_file(data_dir)
        self.required_columns = [
            'eur_usd', 'inventory', 'production', 'rigs',
            'refinery_util', 'gdp', 'inflation', 'wti'
        ]
        self.numeric_columns = [
            'eur_usd', 'inventory', 'production', 'rigs',
            'refinery_util', 'gdp', 'inflation', 'wti'
        ]
        # Format for parsing YYYYMMDD timestamps
        self.date_format = "%Y%m%d"

    def get_latest_file(self, data_dir="data/processed"):
        """Find the most recent processed data file."""

        # Get all processed data files
        data_path = Path(data_dir)
        files = list(data_path.glob("processed_data_*.csv"))
        
        if not files:
            raise ValueError(f"No processed data files found in {data_dir}")
            
        # Extract timestamps and get the latest one
        latest_file = max(files, key=lambda x: x.stem.split('_')[-1])
        logger.info(f"Using latest processed file: {latest_file}")
        
        return latest_file
        
    def validate_data(self, df):
        """Validate input data meets requirements"""
        logger.info("Validating input data...")
        
        # Check required columns
        missing_cols = set(self.required_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Check data types
        for col in self.numeric_columns:
            if not np.issubdtype(df[col].dtype, np.number):
                raise ValueError(f"Column {col} must be numeric")
                
        # Check for missing values
        # if df.isnull().any().any():
        #     raise ValueError("Dataset contains missing values")
            
        # Verify monthly frequency
        dates = pd.to_datetime(df['date'])
        date_diffs = dates.diff()[1:]  # Skip first row which will be NaT
        if not all(diff.days >= 28 and diff.days <= 31 for diff in date_diffs):
            raise ValueError("Data does not have monthly frequency")
            
        logger.info("Data validation completed successfully")
        return True
        
    def remove_features(self, df):
        """Remove low correlation features"""
        logger.info("Removing low correlation features...")
        
        columns_to_drop = ['gdp', 'refinery_util']
        df = df.drop(columns=columns_to_drop)
        
        logger.info(f"Dropped columns: {columns_to_drop}")
        return df
        
    def engineer_features(self, df):
        """Add engineered features"""
        logger.info("Engineering new features...")
        
        # Convert date to datetime if not already
        df['date'] = pd.to_datetime(df['date'])
        
        # Add rolling means
        df['wti_6m_rolling'] = df['wti'].rolling(window=6).mean()
        df['wti_12m_rolling'] = df['wti'].rolling(window=12).mean()
        
        # Add price lag
        df['wti_6m_lag'] = df['wti'].shift(6)
        
        logger.info("Feature engineering completed")
        return df
        
    def handle_rolling_windows(self, df):
        """Handle NaN values from rolling calculations"""
        logger.info("Handling rolling window data...")
        
        # Drop first 12 months of data to account for 12-month rolling mean
        df = df.iloc[12:].copy()
        
        # Verify no NaN values remain
        if df.isnull().any().any():
            raise ValueError("NaN values remain after dropping initial rows")
            
        # Reset index
        df = df.reset_index(drop=True)
        
        logger.info("Rolling window handling completed")
        return df

    def reorder_columns(self, df):
        """Reorder columns to place 'wti' as the last column (target variable)"""
        logger.info("Reordering columns to place target variable 'wti' at the end...")
        
        # Get all columns except 'wti'
        cols = [col for col in df.columns if col != 'wti']
        # Add 'wti' at the end
        cols.append('wti')
        
        # Reorder DataFrame columns
        df = df[cols]
        
        logger.info("Column reordering completed")
        return df
        
    def run_quality_checks(self, df):
        """Run final quality checks on processed data"""
        logger.info("Running quality checks...")
        
        # Check for missing values
        if df.isnull().any().any():
            raise ValueError("Final dataset contains missing values")
            
        # Check date continuity
        dates = pd.to_datetime(df['date'])
        date_diffs = dates.diff()[1:]
        if not all(diff.days >= 28 and diff.days <= 31 for diff in date_diffs):
            raise ValueError("Dates are not continuous in final dataset")
            
        # Basic range checks for engineered features
        if df['wti_6m_rolling'].min() < 0 or df['wti_12m_rolling'].min() < 0:
            raise ValueError("Rolling means contain negative values")
            
        logger.info("Quality checks passed successfully")
        return True
        
    def save_output(self, df, output_dir="data/training_ready"):
        """Save processed data to output directory"""
        logger.info("Saving processed data...")
        
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save versioned file
        date_str = datetime.now().strftime("%Y%m%d")
        output_file = output_path / f"training_data_{date_str}.csv"
        df.to_csv(output_file, index=False)
        
        logger.info(f"Data saved to {output_file}")
        return True
        
    def process(self):
        """Run the full feature processing pipeline"""
        logger.info("Starting feature processing pipeline...")
        
        # Read input data
        df = pd.read_csv(self.input_path)
        
        # Run pipeline steps
        self.validate_data(df)
        df = self.remove_features(df)
        df = self.engineer_features(df)
        df = self.handle_rolling_windows(df)
        df = self.reorder_columns(df)
        self.run_quality_checks(df)
        self.save_output(df)
        
        logger.info("Feature processing pipeline completed successfully")
        return df

if __name__ == "__main__":
    processor = FeatureProcessor()
    processed_data = processor.process()