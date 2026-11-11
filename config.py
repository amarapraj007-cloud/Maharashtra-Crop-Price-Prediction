"""
=====================================================
Maharashtra Crop Price Prediction Dashboard
CONFIG FILE — सगळ्या settings इथे आहेत
=====================================================
एकाच ठिकाणी बदल करायला सोपं म्हणून config file बनवली आहे
"""

# =====================================================
# DATABASE CONFIG — MySQL Connection
# =====================================================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",      # ← तुमचा MySQL password टाका
    "database": "crop_price_db",
    "port": 3306
}

# SQLAlchemy connection string
DB_URL = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"


# =====================================================
# CROPS — आपण track करणारे 5 crops
# =====================================================
CROPS = ["Onion", "Tomato", "Soybean", "Cotton", "Gram"]

CROP_NAMES_MR = {
    "Onion": "कांदा",
    "Tomato": "टोमॅटो",
    "Soybean": "सोयाबीन",
    "Cotton": "कापूस",
    "Gram": "हरभरा"
}

# Typical price ranges per crop (₹/Quintal) — for sample data generation
CROP_PRICE_RANGES = {
    "Onion":   {"min": 200,  "max": 2500, "base": 800,  "volatility": 300},
    "Tomato":  {"min": 200,  "max": 3000, "base": 1000, "volatility": 400},
    "Soybean": {"min": 2000, "max": 6000, "base": 3800, "volatility": 500},
    "Cotton":  {"min": 4000, "max": 8000, "base": 5800, "volatility": 800},
    "Gram":    {"min": 3000, "max": 7000, "base": 5000, "volatility": 600}
}

# Seasonal multipliers (which months prices are higher/lower)
# Month: 1=Jan, 2=Feb, ... 12=Dec
SEASONAL_MULTIPLIER = {
    "Onion":   {1:1.3, 2:1.4, 3:1.2, 4:0.9, 5:0.7, 6:0.6, 7:0.7, 8:0.8, 9:0.9, 10:1.1, 11:1.2, 12:1.3},
    "Tomato":  {1:1.2, 2:1.1, 3:0.9, 4:0.7, 5:0.6, 6:0.8, 7:1.0, 8:1.1, 9:1.2, 10:1.3, 11:1.1, 12:1.0},
    "Soybean": {1:1.1, 2:1.0, 3:1.0, 4:0.9, 5:0.9, 6:0.8, 7:0.9, 8:1.0, 9:1.2, 10:1.3, 11:1.1, 12:1.0},
    "Cotton":  {1:1.0, 2:1.0, 3:1.0, 4:0.9, 5:0.9, 6:0.8, 7:0.9, 8:1.0, 9:1.2, 10:1.3, 11:1.2, 12:1.0},
    "Gram":    {1:1.1, 2:1.1, 3:1.0, 4:0.9, 5:0.8, 6:0.9, 7:1.0, 8:1.0, 9:1.1, 10:1.2, 11:1.1, 12:1.0}
}


# =====================================================
# MARKETS — 10 Major Mandis
# =====================================================
MARKETS = [
    {"market_name": "Lasalgaon", "district": "Nashik"},
    {"market_name": "Pimpalgaon", "district": "Nashik"},
    {"market_name": "Nanded", "district": "Nanded"},
    {"market_name": "Latur", "district": "Latur"},
    {"market_name": "Jalgaon", "district": "Jalgaon"},
    {"market_name": "Aurangabad", "district": "Aurangabad"},
    {"market_name": "Solapur", "district": "Solapur"},
    {"market_name": "Amravati", "district": "Amravati"},
    {"market_name": "Dhule", "district": "Dhule"},
    {"market_name": "Kolhapur", "district": "Kolhapur"}
]


# =====================================================
# DATA GENERATION — Sample data settings
# =====================================================
DAYS_OF_HISTORY = 180    # How many days of historical data to generate
RANDOM_SEED = 42         # For reproducible results


# =====================================================
# ML MODEL — Training Settings
# =====================================================
MODEL_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "n_estimators": 100,       # Random Forest trees
    "max_depth": 10,
    "prediction_days": 7,      # Predict next 7 days
    "lag_days": 7,             # Use last 7 days as features
    "model_version": "v1.0"
}


# =====================================================
# EMAIL ALERT — SMTP Settings
# =====================================================
EMAIL_CONFIG = {
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password",    # Gmail App Password
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "recipient_email": "recipient_email@gmail.com",
    "enabled": False      # True करा जेव्हा email alert चालू करायचे
}


# =====================================================
# ALERT THRESHOLDS — कधी alert पाठवायचा
# =====================================================
ALERT_THRESHOLDS = {
    "PRICE_DROP_PCT": -15,     # 15% किंवा जास्त price drop झाला तर alert
    "PRICE_SPIKE_PCT": 25,     # 25% किंवा जास्त price spike झाला तर alert
}


# =====================================================
# FILE PATHS — Data files
# =====================================================
DATA_DIR = "../data/"
RAW_DATA_FILE = "../data/raw_crop_prices.csv"
PROCESSED_DATA_FILE = "../data/processed_crop_prices.csv"
PREDICTIONS_FILE = "../data/predictions.csv"
MODELS_DIR = "../models/"


# =====================================================
# AGMARKNET — Web Scraping Settings (Future Use)
# =====================================================
AGMARKNET_CONFIG = {
    "base_url": "https://agmarknet.gov.in/SearchCmmMkt.aspx",
    "state": "Maharashtra",
    "scraping_enabled": False,    # True करा जेव्हा real scraping करायचे
    "request_delay": 2,          # Seconds between requests (don't overload server)
    "timeout": 30
}
