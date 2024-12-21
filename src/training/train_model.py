import pandas as pd
import numpy as np
import joblib
import logging
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        # Define base directories
        self.data_dir = 'data/training_ready'
        self.models_dir = 'models'
        self.output_dir = 'results'
        self.plots_dir = os.path.join(self.output_dir, 'plots')
        
        # Get date stamp (YYYYMMDD only)
        self.datestamp = datetime.now().strftime('%Y%m%d')
        
        # Get latest training data file
        self.data_path = self._get_latest_file(
            self.data_dir, 
            prefix='training_data_', 
            suffix='.csv'
        )
        if not self.data_path:
            raise FileNotFoundError(f"No training data files found in {self.data_dir}")
            
        # Get latest model directory
        latest_model_dir, model_timestamp = self._get_latest_model_dir()
            
        # Construct paths for model and scaler
        self.model_path = os.path.join(latest_model_dir, f"best_model_{model_timestamp}.joblib")
        self.scaler_path = os.path.join(latest_model_dir, f"scaler_{model_timestamp}.joblib")
        
        # Create output directories
        os.makedirs(self.plots_dir, exist_ok=True)
        
        logging.info(f"Initialized ModelTrainer for date: {self.datestamp}")
        logging.info(f"Using model: {self.model_path}")
        logging.info(f"Using scaler: {self.scaler_path}")
        logging.info(f"Using training data: {self.data_path}")

    def _get_latest_file(self, directory, prefix='', suffix=''):
        """Get the latest file with given prefix and suffix from directory."""
        matching_files = [
            f for f in os.listdir(directory)
            if f.startswith(prefix) and f.endswith(suffix)
        ]
        
        if not matching_files:
            return None
            
        matching_files.sort(key=lambda x: x.replace(prefix, '').replace(suffix, ''))
        return os.path.join(directory, matching_files[-1])

    def _get_latest_model_dir(self):
        """Get the path to latest timestamped models directory."""
        try:
            model_dirs = [
                d for d in os.listdir(self.models_dir)
                if os.path.isdir(os.path.join(self.models_dir, d))
                and d.startswith('models_')
            ]
            
            if not model_dirs:
                raise FileNotFoundError("No model directories found")
                
            latest_dir = sorted(model_dirs)[-1]
            timestamp = latest_dir.split('_')[1]
            
            return os.path.join(self.models_dir, latest_dir), timestamp
            
        except Exception as e:
            logger.error(f"Error finding latest model directory: {str(e)}")
            raise

    def load_and_prepare_data(self):
        """Load and prepare data for training."""
        try:
            logger.info("Loading and preparing data...")
            df = pd.read_csv(self.data_path)
            
            features = ['eur_usd', 'inventory', 'production', 'rigs', 'inflation', 
                       'wti_6m_rolling', 'wti_12m_rolling', 'wti_6m_lag']
            
            # Verify features
            missing_features = [f for f in features if f not in df.columns]
            if missing_features:
                raise ValueError(f"Missing required features: {missing_features}")
            
            X = df[features]
            y = df['wti']
            
            # Load and apply scaler
            scaler = joblib.load(self.scaler_path)
            X_scaled = scaler.transform(X)
            
            # Split data - using last 20% for testing
            split_idx = int(len(df) * 0.8)
            X_train = X_scaled[:split_idx]
            X_test = X_scaled[split_idx:]
            y_train = y[:split_idx]
            y_test = y[split_idx:]
            
            return X_train, X_test, y_train, y_test, df['date'].values, scaler
            
        except Exception as e:
            logger.error(f"Error in data preparation: {str(e)}")
            raise

    def train_model(self, X_train, X_test, y_train, y_test):
        """Train model and calculate metrics."""
        try:
            logger.info("Loading and training model...")
            model = joblib.load(self.model_path)
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            # Calculate metrics
            metrics = {
                'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'train_mae': mean_absolute_error(y_train, y_pred_train),
                'test_mae': mean_absolute_error(y_test, y_pred_test),
                'train_mape': np.mean(np.abs((y_train - y_pred_train) / y_train)) * 100,
                'test_mape': np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100,
                'train_da': np.mean(np.sign(np.diff(y_train)) == 
                                  np.sign(np.diff(y_pred_train))) * 100,
                'test_da': np.mean(np.sign(np.diff(y_test)) == 
                                 np.sign(np.diff(y_pred_test))) * 100
            }
            
            return model, metrics, (y_pred_train, y_pred_test)
            
        except Exception as e:
            logger.error(f"Error in model training: {str(e)}")
            raise

    def save_results(self, metrics, dates, y_train, y_test, y_pred_train, y_pred_test):
        """Save metrics and generate plots with date stamp."""
        try:
            # Save metrics with datestamp
            metrics_file = os.path.join(self.output_dir, f'metrics_{self.datestamp}.txt')
            with open(metrics_file, 'w') as f:
                f.write(f"Metrics Report - Generated on {self.datestamp}\n\n")
                f.write("Training Set Metrics:\n")
                f.write(f"RMSE: {metrics['train_rmse']:.2f}\n")
                f.write(f"MAE: {metrics['train_mae']:.2f}\n")
                f.write(f"MAPE: {metrics['train_mape']:.2f}%\n")
                f.write(f"Directional Accuracy: {metrics['train_da']:.2f}%\n\n")
                f.write("Test Set Metrics:\n")
                f.write(f"RMSE: {metrics['test_rmse']:.2f}\n")
                f.write(f"MAE: {metrics['test_mae']:.2f}\n")
                f.write(f"MAPE: {metrics['test_mape']:.2f}%\n")
                f.write(f"Directional Accuracy: {metrics['test_da']:.2f}%\n")
            
            # Generate plots
            split_idx = len(y_train)
            dates_train = dates[:split_idx]
            dates_test = dates[split_idx:]

            # Convert dates to datetime if they aren't already
            dates_            # Generate plots
            split_idx = len(y_train)
            dates_train = dates[:split_idx]
            dates_test = dates[split_idx:]train = pd.to_datetime(dates_train)
            dates_test = pd.to_datetime(dates_test)

            # Training predictions plot
            plt.figure(figsize=(12, 6))
            plt.plot(dates_train, y_train, label='Actual', color='blue')
            plt.plot(dates_train, y_pred_train, label='Predicted', color='red', linestyle='--')
            plt.title(f'Training Set: Actual vs Predicted WTI Prices\nGenerated: {self.datestamp}')
            plt.xlabel('Date')
            plt.ylabel('Price (USD)')

            # Format x-axis to show only year and month
            plt.gca().xaxis.set_major_locator(mdates.YearLocator(2))  # Show every 2 years
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.xticks(rotation=45, ha='right')  # Rotate and align the tick labels
            plt.grid(True, alpha=0.3)  # Add light grid
            plt.margins(x=0.02)  # Reduce blank space on sides
            plt.legend(loc='upper right')
            plt.tight_layout()
            plt.savefig(os.path.join(self.plots_dir, f'training_predictions_{self.datestamp}.png'))
            plt.close()

            # Test predictions plot (similar modifications)
            plt.figure(figsize=(12, 6))
            plt.plot(dates_test, y_test, label='Actual', color='blue')
            plt.plot(dates_test, y_pred_test, label='Predicted', color='red', linestyle='--')
            plt.title(f'Test Set: Actual vs Predicted WTI Prices\nGenerated: {self.datestamp}')
            plt.xlabel('Date')
            plt.ylabel('Price (USD)')

            # Format x-axis to show only year and month
            plt.gca().xaxis.set_major_locator(mdates.YearLocator(1))  # Show every year for test set
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            plt.xticks(rotation=45, ha='right')
            plt.grid(True, alpha=0.3)
            plt.margins(x=0.02)
            plt.legend(loc='upper right')
            plt.tight_layout()
            plt.savefig(os.path.join(self.plots_dir, f'test_predictions_{self.datestamp}.png'))
            plt.close()
            
            logger.info(f"Results saved with datestamp {self.datestamp}")
            logger.info(f"Metrics saved to {metrics_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            raise

def main():
    try:
        trainer = ModelTrainer()
        
        # Load and prepare data
        X_train, X_test, y_train, y_test, dates, scaler = trainer.load_and_prepare_data()
        
        # Train model and get predictions
        model, metrics, (y_pred_train, y_pred_test) = trainer.train_model(
            X_train, X_test, y_train, y_test
        )
        
        # Save results with datestamp
        trainer.save_results(metrics, dates, y_train, y_test, y_pred_train, y_pred_test)
        
        logger.info("Training pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()