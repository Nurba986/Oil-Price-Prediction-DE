# Detailed Setup Guide

## Development Environment Setup

### 1. Python Environment
Ensure you have Python 3.8+ installed:
```bash
python --version
```

### 2. Project Setup
```bash
# Create project directory
mkdir oil_price_prediction
cd oil_price_prediction

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install pandas python-dotenv requests
pip freeze > requirements.txt
```

### 3. Project Structure
Create the following directory structure:
```bash
# Create directories
mkdir -p src/collectors src/processors src/utils
mkdir -p tests data/raw data/processed
mkdir config notebooks
```

### 4. Environment Configuration
1. Get your EIA API key from [EIA Open Data](https://www.eia.gov/opendata/)
2. Create .env file:
```bash
echo "EIA_API_KEY=your-api-key-here" > .env
```

### 5. Git Setup
```bash
# Initialize git repository
git init

# Create .gitignore
cat > .gitignore << EOL
# Environment variables
.env

# Python
__pycache__/
*.py[cod]
venv/

# Data
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# IDE
.vscode/
.idea/
EOL

# Initial commit
git add .
git commit -m "Initial project setup"
```

## Verification Steps

### 1. Test Environment
```bash
# Verify Python environment
python -c "import pandas, dotenv, requests; print('All packages installed')"
```

### 2. Test API Connection
```bash
# Run the EIA collector
python -m src.collectors.eia_collector
```

### 3. Common Issues and Solutions

#### API Key Issues
- Ensure .env file is in root directory
- Verify API key format
- Check file permissions

#### Import Errors
- Verify virtual environment is activated
- Check package installation
- Confirm Python path includes project root

## Development Workflow

### 1. Code Organization
- Put collection logic in src/collectors/
- Add processing code in src/processors/
- Place shared utilities in src/utils/

### 2. Testing
- Write tests in tests/ directory
- Run tests before commits
- Document test coverage

### 3. Data Management
- Store raw data in data/raw/
- Save processed data in data/processed/
- Document data schemas

## Next Steps
1. Implement data validation
2. Add error logging
3. Set up automated testing
4. Plan cloud deployment