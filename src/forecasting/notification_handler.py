import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NotificationHandler:
    def __init__(self):
        """Initialize notification handler."""
        self.project_root = self._get_project_root()
        self.forecasts_dir = self.project_root / 'results' / 'forecasts'
        self.plots_dir = self.project_root / 'results' / 'plots'
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        
        # Email configuration
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def _get_project_root(self):
        """Get the project root directory."""
        current_dir = Path(os.getcwd())
        while not (current_dir / '.env').exists():
            current_dir = current_dir.parent
            if current_dir == current_dir.parent:
                raise FileNotFoundError("Project root not found")
        return current_dir

    def _get_latest_forecast(self):
        """Get the latest forecast JSON file."""
        try:
            json_files = list(self.forecasts_dir.glob('wti_forecast_*.json'))
            if not json_files:
                raise FileNotFoundError("No forecast files found")
                
            latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file, 'r') as f:
                forecast_data = json.load(f)
                
            logger.info(f"Loaded latest forecast from {latest_file}")
            return forecast_data
            
        except Exception as e:
            logger.error(f"Error loading forecast data: {str(e)}")
            raise

    def _create_forecast_plot(self, forecast_data):
        """Create forecast visualization plot."""
        try:
            # Extract data
            dates = [f['forecast_date'] for f in forecast_data['forecasts']]
            prices = [f['predicted_price'] for f in forecast_data['forecasts']]
            lower_bounds = [f['confidence_interval']['lower'] for f in forecast_data['forecasts']]
            upper_bounds = [f['confidence_interval']['upper'] for f in forecast_data['forecasts']]
            
            # Create plot
            plt.figure(figsize=(8, 6))
            
            # Plot predicted prices
            plt.plot(dates, prices, marker='o', label='Predicted Price')
            
            # Plot confidence intervals
            plt.fill_between(dates, lower_bounds, upper_bounds, alpha=0.2, label='Confidence Interval')
            
            # Add current price point
            plt.scatter(dates[0], forecast_data['current_wti'], color='red', marker='*', 
                      s=150, label='Current Price')
            
            # Customize plot
            plt.title('WTI Price Forecast with Confidence Intervals')
            plt.xlabel('Date')
            plt.ylabel('Price (USD)')
            plt.xticks(rotation=0)
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Save plot
            plot_path = self.plots_dir / f'forecast_plot_{datetime.now().strftime("%Y%m%d")}.png'
            plt.savefig(plot_path, bbox_inches='tight', dpi=300)
            plt.close()
            
            logger.info(f"Created forecast plot at {plot_path}")
            return plot_path
            
        except Exception as e:
            logger.error(f"Error creating forecast plot: {str(e)}")
            raise

    def _create_email_content(self, forecast_data):
        """Create HTML email content with forecast data."""
        html_content = f"""
        <html>
        <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                .header {{
                    color: #333;
                    margin-bottom: 20px;
                }}
                .current-price {{
                    font-size: 18px;
                    color: #333;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>WTI Price Forecast Update</h2>
            </div>
            
            <div class="current-price">
                Current WTI Price: ${forecast_data['current_wti']:.2f}
            </div>
            
            <table>
                <tr>
                    <th>Date</th>
                    <th>Predicted Price</th>
                    <th>Range</th>
                    <th>Confidence</th>
                </tr>
        """
        
        # Add forecast rows
        for forecast in forecast_data['forecasts']:
            html_content += f"""
                <tr>
                    <td>{forecast['forecast_date']}</td>
                    <td>${forecast['predicted_price']:.2f}</td>
                    <td>${forecast['confidence_interval']['lower']:.2f} - ${forecast['confidence_interval']['upper']:.2f}</td>
                    <td>{forecast['confidence']:.1f}%</td>
                </tr>
            """
            
        html_content += """
            </table>
            <p>* Forecast chart attached below</p>
        </body>
        </html>
        """
        
        return html_content

    def send_notification(self):
        """Send email notification with forecast data."""
        try:
            # Validate email configuration
            if not all([self.sender_email, self.sender_password, self.recipient_email]):
                raise ValueError("Missing required email configuration. Check SENDER_EMAIL, SENDER_PASSWORD and RECIPIENT_EMAIL in .env file")

            # Get forecast data
            forecast_data = self._get_latest_forecast()
            
            # Create visualization
            plot_path = self._create_forecast_plot(forecast_data)
            
            # Create email message
            msg = MIMEMultipart('related')
            msg['Subject'] = "WTI Price Prediction Update"
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Add HTML content
            html_content = self._create_email_content(forecast_data)
            msg.attach(MIMEText(html_content, 'html'))
            
            # Add plot image
            with open(plot_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<forecast_plot>')
                msg.attach(img)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                
                # Validate recipient email
                if not self.recipient_email or '@' not in self.recipient_email:
                    raise ValueError(f"Invalid recipient email address: {self.recipient_email}")
                    
                server.send_message(msg)
                    
            logger.info(f"Successfully sent forecast notification email to {self.recipient_email}")
                
        except smtplib.SMTPAuthenticationError:
            logger.error("Failed to authenticate with SMTP server. Please check your email credentials.")
            raise
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Failed to send email - recipient refused: {str(e)}")
            raise
        except ValueError as ve:
            logger.error(f"Configuration error: {str(ve)}")
            raise
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        handler = NotificationHandler()
        handler.send_notification()
    except Exception as e:
        logger.error(f"Notification pipeline failed: {str(e)}")
        raise