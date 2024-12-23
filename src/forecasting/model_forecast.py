import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime, timedelta
import logging
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WTIForecaster:
    def __init__(self):
        """Initialize the WTI price forecaster."""
        self.project_root = self._get_project_root()
        
        # Set up paths
        self.models_dir = self.project_root / 'models'
        self.data_dir = self.project_root / 'data' / 'training_ready'
        self.output_dir = self.project_root / 'results' / 'forecasts'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load latest model artifacts
        self.model, self.scaler = self._load_latest_model()
        self.training_data = self._load_latest_training_data()
        
        # Define confidence decay parameters
        self.base_confidence = 0.8  # 80% base confidence
        self.confidence_decay = 0.15  # 15% decay per month
        
        # Define forecast horizons (in months)
        self.forecast_horizons = [1, 2, 3]  # 1-3 months ahead

    def _get_project_root(self):
        """Get the project root directory."""
        current_dir = Path(os.getcwd())
        while not (current_dir / '.env').exists():
            current_dir = current_dir.parent
            if current_dir == current_dir.parent:
                raise FileNotFoundError("Project root not found")
        return current_dir

    def _get_latest_model_dir(self):
        """Get the latest model directory based on timestamp."""
        model_dirs = [d for d in self.models_dir.iterdir() if d.is_dir() and d.name.startswith('models_')]
        if not model_dirs:
            raise FileNotFoundError("No model directories found")
        return max(model_dirs, key=lambda x: x.name.split('_')[1])

    def _load_latest_model(self):
        """Load the latest model and scaler."""
        try:
            latest_model_dir = self._get_latest_model_dir()
            timestamp = latest_model_dir.name.split('_')[1]
            
            model_path = latest_model_dir / f'best_model_{timestamp}.joblib'
            scaler_path = latest_model_dir / f'scaler_{timestamp}.joblib'
            
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            
            logger.info(f"Loaded model and scaler from {latest_model_dir}")
            return model, scaler
            
        except Exception as e:
            logger.error(f"Error loading model artifacts: {str(e)}")
            raise

    def _load_latest_training_data(self):
        """Load the latest training data."""
        try:
            # List all training data files
            data_files = list(self.data_dir.glob('training_data_*.csv'))
            if not data_files:
                raise FileNotFoundError("No training data files found")
                
            # Get latest file by comparing the timestamp in filename
            latest_file = max(data_files, 
                            key=lambda x: datetime.strptime(
                                x.name.split('_')[2].split('.')[0], 
                                '%Y%m%d'
                            ))
            
            # Read the CSV file
            df = pd.read_csv(latest_file)
            logger.info(f"Loaded training data from {latest_file}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading training data: {str(e)}")
            raise

    def _convert_to_serializable(self, obj):
        """Convert numpy types to Python native types for JSON serialization."""
        if isinstance(obj, (np.int8, np.int16, np.int32, np.int64,
                        np.uint8, np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    def _prepare_features(self, current_data):
        """Prepare features for forecasting."""
        required_features = [
            'eur_usd', 'inventory', 'production', 'rigs',
            'inflation', 'wti_6m_rolling', 'wti_12m_rolling', 'wti_6m_lag'
        ]      
       
        # Ensure all required features are present
        missing_features = set(required_features) - set(current_data.columns)
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
            
        return current_data[required_features].copy()

    def _calculate_confidence(self, horizon):
        """Calculate confidence score based on forecast horizon."""
        confidence = self.base_confidence - (horizon * self.confidence_decay)
        return max(0.1, min(1.0, confidence))  # Clamp between 0.1 and 1.0

    def _calculate_error_margin(self, confidence, std_dev):
        """Calculate error margin based on confidence and historical volatility."""
        # Use historical volatility (std dev) and confidence to estimate margin
        z_score = {0.8: 1.28, 0.65: 0.93, 0.5: 0.67}  # Approximate z-scores
        closest_conf = min(z_score.keys(), key=lambda x: abs(x - confidence))
        return z_score[closest_conf] * std_dev

    def generate_forecast(self):
        """Generate WTI price forecasts for the next 3 months."""
        try:
            # Load latest model and data
            current_data = self._load_latest_training_data()
            
            # Get current WTI price (most recent value)
            current_wti = current_data['wti'].iloc[-1]
            
            # Prepare features for prediction
            forecast_features = self._prepare_features(current_data)
            X_forecast = self.scaler.transform(forecast_features.iloc[-1:])
            
            # Make prediction for next 3 months
            predictions = []
            confidence_intervals = {'lower': [], 'upper': []}
            
            for i in range(3):  # Generate 3 months of forecasts
                pred = self.model.predict(X_forecast)[0]
                predictions.append(float(pred))  # Convert to float for JSON serialization
                
                # Calculate confidence score and intervals
                confidence = self._calculate_confidence(i + 1)  # Decreasing confidence for further months
                std_dev = current_data['wti'].std()
                error_margin = self._calculate_error_margin(confidence, std_dev)
                
                confidence_intervals['lower'].append(float(pred - error_margin))
                confidence_intervals['upper'].append(float(pred + error_margin))
                
                # Update features for next prediction
                # You might want to update relevant features here
            
            # Generate forecast dates
            last_date = pd.to_datetime(current_data['date'].iloc[-1])
            forecast_dates = [(last_date + pd.DateOffset(months=i+1)).strftime('%Y-%m-%d') 
                            for i in range(3)]
            
            # Prepare results
            forecast_results = {
                'current_wti': float(current_wti),
                'forecasts': [
                    {
                        'forecast_date': date,
                        'predicted_price': pred,
                        'confidence_interval': {
                            'lower': low,
                            'upper': high
                        },
                        'confidence': (1 - (i * 0.15)) * 100  # Decreasing confidence: 80%, 65%, 50%
                    }
                    for i, (date, pred, low, high) in enumerate(zip(
                        forecast_dates, predictions,
                        confidence_intervals['lower'],
                        confidence_intervals['upper']
                    ))
                ]
            }
            
            # Save results
            timestamp = datetime.now().strftime('%Y%m%d')
            output_file = self.output_dir / f'wti_forecast_{timestamp}.json'
            
            with open(output_file, 'w') as f:
                json.dump(forecast_results, f, indent=4)
                
            logger.info(f"Generated and saved 3-month forecasts to {output_file}")
            return forecast_results
            
        except Exception as e:
            logger.error(f"Error generating forecasts: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        forecaster = WTIForecaster()
        forecasts = forecaster.generate_forecast()
        
        # Print forecasts
        print("\nWTI Price Forecasts:")
        print(f"Current Price: ${forecasts['current_wti']}")
        print("\nForecasts:")
        for f in forecasts['forecasts']:
            print(f"Date: {f['forecast_date']}")
            print(f"Price: ${f['predicted_price']:.2f} (${f['confidence_interval']['lower']:.2f} - ${f['confidence_interval']['upper']:.2f})")
            print(f"Confidence: {f['confidence']:.1f}%\n")
            
    except Exception as e:
        logger.error(f"Forecasting pipeline failed: {str(e)}")
        raise