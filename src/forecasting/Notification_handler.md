notification_handler.py

def send_email_report():
    # Read saved metrics
    # Load saved PNG/JPEG files 'results/plots/'
    # Attach images to email
    email.attach('test_predictions.png')
    email.attach('training_predictions.png')
    # Format email content with metrics
        Subject: WTI Price Prediction Update

        Prediction Details:
        - Forecasted Price: $XX.XX
        - Confidence Level: XX%
        - Prediction Period: Next 12 months
        - Model Performance Metrics: RMSE: XX.XX

        Key Insights:
        - Trend Direction: Up/Down
        - Add visualizations result/plots
        - Handle email sending
        - Better for maintenance/updates
        - Separates concerns clearly
 
    # Send_email(
        subject="WTI Price Prediction Ready",
        body=f"Predicted price: ${predictions[0]:.2f}"
    )