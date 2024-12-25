"""
Pipeline orchestrator script that coordinates the execution of data pipeline components.
Scheduled to run every Thursday at 5 PM Chicago time.
"""

import os
import sys
from pathlib import Path
import subprocess
import schedule
import time
import pytz
from datetime import datetime
import logging

# Create logs directory if it doesn't exist
current_dir = Path(__file__).parent
logs_dir = current_dir / 'logs'
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    def __init__(self):
        """Initialize orchestrator with project paths."""
        self.project_root = self._get_project_root()
        
        # Set up paths for different components
        self.src_dir = self.project_root / 'src'
        self.collectors_dir = self.src_dir / 'collectors'
        self.processors_dir = self.src_dir / 'processors'
        self.forecasting_dir = self.src_dir / 'forecasting'

        # Set up logging directory
        self.logs_dir = self.project_root / 'logs'
        self.logs_dir.mkdir(exist_ok=True)

    def _get_project_root(self):
        """Get the project root directory by traversing up until finding .env file."""
        current_dir = Path(os.getcwd())
        while not (current_dir / '.env').exists():
            parent = current_dir.parent
            if parent == current_dir:
                raise FileNotFoundError("Project root not found (no .env file)")
            current_dir = parent
        return current_dir

    def run_script(self, script_path, script_name):
        """Execute a Python script and handle errors."""
        try:
            logger.info(f"Starting {script_name}")
            start_time = time.time()
            
            # Set working directory to project root before running script
            os.chdir(str(self.project_root))
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                check=True,
                capture_output=True,
                text=True,
                cwd=str(self.project_root)  # Set working directory for subprocess
            )
            
            execution_time = time.time() - start_time
            logger.info(f"Successfully completed {script_name} in {execution_time:.2f} seconds")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running {script_name}: {str(e)}")
            logger.error(f"Script output: {e.output}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error running {script_name}: {str(e)}")
            return False

    def run_collection_pipeline(self):
        """Run all data collection scripts."""
        collection_scripts = [
            (self.collectors_dir / 'collector_eia.py', 'EIA Collector'),
            (self.collectors_dir / 'collector_fred.py', 'FRED Collector'),
            (self.collectors_dir / 'web_scrap_eia.py', 'EIA Web Scraper'),
            (self.collectors_dir / 'web_scrap_inflation.py', 'Inflation Web Scraper')
        ]

        logger.info("Starting data collection pipeline")
        for script_path, script_name in collection_scripts:
            if not self.run_script(script_path, script_name):
                logger.error(f"Collection pipeline failed at {script_name}")
                return False
        logger.info("Data collection pipeline completed successfully")
        return True

    def run_processing_pipeline(self):
        """Run data and feature processing scripts."""
        processing_scripts = [
            (self.processors_dir / 'processor_data.py', 'Data Processor'),
            (self.processors_dir / 'processor_feature.py', 'Feature Processor')
        ]

        logger.info("Starting data processing pipeline")
        for script_path, script_name in processing_scripts:
            if not self.run_script(script_path, script_name):
                logger.error(f"Processing pipeline failed at {script_name}")
                return False
        logger.info("Data processing pipeline completed successfully")
        return True

    def run_forecasting_pipeline(self):
        """Run forecasting and notification scripts."""
        forecasting_scripts = [
            (self.forecasting_dir / 'model_forecast.py', 'Model Forecaster'),
            (self.forecasting_dir / 'notification_handler.py', 'Notification Handler')
        ]

        logger.info("Starting forecasting pipeline")
        for script_path, script_name in forecasting_scripts:
            if not self.run_script(script_path, script_name):
                logger.error(f"Forecasting pipeline failed at {script_name}")
                return False
        logger.info("Forecasting pipeline completed successfully")
        return True

    def run_full_pipeline(self):
        """Execute the complete pipeline from collection to notification."""
        try:
            chicago_tz = pytz.timezone('America/Chicago')
            current_time = datetime.now(chicago_tz)
            logger.info(f"Starting full pipeline execution at {current_time}")

            # Execute each pipeline stage
            stages = [
                (self.run_collection_pipeline, "Data Collection"),
                (self.run_processing_pipeline, "Data Processing"),
                (self.run_forecasting_pipeline, "Forecasting and Notification")
            ]

            for stage_func, stage_name in stages:
                logger.info(f"Starting pipeline stage: {stage_name}")
                if not stage_func():
                    raise Exception(f"Pipeline failed during {stage_name}")
                logger.info(f"Completed pipeline stage: {stage_name}")

            execution_time = time.time() - current_time.timestamp()
            logger.info(f"Full pipeline completed successfully in {execution_time:.2f} seconds")
            return True

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            return False

def main():
    """Main function to set up and run the scheduler."""
    try:
        orchestrator = PipelineOrchestrator()
        
        # Run pipeline immediately for testing
        logger.info("Running pipeline for testing...")
        orchestrator.run_full_pipeline()
        
        # After testing, uncomment these lines for scheduled execution
        schedule.every().thursday.at("17:00").do(orchestrator.run_full_pipeline)
        logger.info("Scheduler started - Pipeline will run every Thursday at 5 PM Chicago time")
        logger.info("Press Ctrl+C to stop the scheduler")
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()