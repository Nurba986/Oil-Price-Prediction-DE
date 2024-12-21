Create modular functions
Make pipeline classes
Add error handling
Include logging

# train_model.py
def load_and_prepare_data():
    # Load training_data_20241219.csv
    # Apply scaler_20241219.joblib
    # Split data (train/test)
    pass

def train_model():
    # Load best_model_20241219.joblib
    # Train model - future prediction
    # Validate performance
    pass

def save_results():
    # Clear old results first
    clear_old_results()  # Delete old PNGs, metrics files if exist
    # Save metrics() # New metrics
    # generate_plots() Generate visualizations(charts/plots), basic charts showing predictions and trends. plt.savefig('plots/prediction_trend.png')
    # commented for future using API response return {"predicted_price": predictions[0]} not used now, for future

def main():
    # 1. Load & prepare data
    data = load_and_prepare_data()    
    # 2. Train & validate
    model, metrics = train_model()    
    # 3. Save everything & visualize
    save_results()

if __name__ == "__main__":
    main()

