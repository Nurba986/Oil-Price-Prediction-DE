Data Latency Handling:
Include confidence scores that decrease with prediction distance
Note: Focus on 3-month forecasts with high confidence,

Prediction Approach:
Focus on shorter-term predictions (1-2-3 months) where confidence is higher
Use moving averages for faster-moving indicators
Forward fill slow-moving indicators
Include confidence scores that decay with time

Implementation Details:
Handle lagged indicators
Prepare features for future predictions
Calculate confidence scores
Make predictions with confidence levels

Flow:
Raw Data -> Data Processor -> Feature Processor -> Training
Raw Data -> Forecast Processor -> Forecasting (using trained model)

Current WTI: $75
Forecasts:
Jan 2025: $85 ±$5 (80% confidence)
Feb 2025: $90 ±$8 (65% confidence)
