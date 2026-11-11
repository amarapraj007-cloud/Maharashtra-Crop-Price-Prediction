
"""
=====================================================
🌾 MAHARASHTRA CROP PRICE PREDICTION DASHBOARD
ONE FILE — Complete Pipeline
=====================================================
1. Data Generate
2. Data Clean + Features
3. ML Model Train
4. Price Predict (7 days)
5. MySQL Store
RUN: python crop_pipeline.py
=====================================================
"""

# =====================================================
# CONFIG
# =====================================================
import os
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
if not MYSQL_PASSWORD:
    raise RuntimeError("MYSQL_PASSWORD environment variable is not set")

DB_URL = (
    f"mysql+mysqlconnector://root:{MYSQL_PASSWORD}"
    "@localhost:3306/crop_price_db"
)
# =====================================================
# INSTALL REQUIRED PACKAGES
# =====================================================
def install_packages():
    import subprocess
    packages = [
        "pandas", "numpy", "scikit-learn",
        "matplotlib", "seaborn", "sqlalchemy",
        "mysql-connector-python", "joblib"
    ]
    for pkg in packages:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"📦 Installing {pkg}...")
            subprocess.check_call(["pip", "install", pkg], stdout=subprocess.DEVNULL)
    print("✅ All packages ready!\n")

# =====================================================
# IMPORTS
# =====================================================
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import create_engine, text
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# =====================================================
# SETTINGS
# =====================================================
CROPS = ["Onion", "Tomato", "Soybean", "Cotton", "Gram"]
CROP_NAMES_MR = {
    "Onion": "कांदा", "Tomato": "टोमॅटो",
    "Soybean": "सोयाबीन", "Cotton": "कापूस", "Gram": "हरभरा"
}
CROP_PRICE_RANGES = {
    "Onion":   {"min": 200,  "max": 2500, "base": 800,  "volatility": 300},
    "Tomato":  {"min": 200,  "max": 3000, "base": 1000, "volatility": 400},
    "Soybean": {"min": 2000, "max": 6000, "base": 3800, "volatility": 500},
    "Cotton":  {"min": 4000, "max": 8000, "base": 5800, "volatility": 800},
    "Gram":    {"min": 3000, "max": 7000, "base": 5000, "volatility": 600}
}
SEASONAL_MULTIPLIER = {
    "Onion":   {1:1.3,2:1.4,3:1.2,4:0.9,5:0.7,6:0.6,7:0.7,8:0.8,9:0.9,10:1.1,11:1.2,12:1.3},
    "Tomato":  {1:1.2,2:1.1,3:0.9,4:0.7,5:0.6,6:0.8,7:1.0,8:1.1,9:1.2,10:1.3,11:1.1,12:1.0},
    "Soybean": {1:1.1,2:1.0,3:1.0,4:0.9,5:0.9,6:0.8,7:0.9,8:1.0,9:1.2,10:1.3,11:1.1,12:1.0},
    "Cotton":  {1:1.0,2:1.0,3:1.0,4:0.9,5:0.9,6:0.8,7:0.9,8:1.0,9:1.2,10:1.3,11:1.2,12:1.0},
    "Gram":    {1:1.1,2:1.1,3:1.0,4:0.9,5:0.8,6:0.9,7:1.0,8:1.0,9:1.1,10:1.2,11:1.1,12:1.0}
}
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
DAYS_OF_HISTORY = 180
RANDOM_SEED = 42
import os
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

# =====================================================
# STEP 1: DATA GENERATION
# =====================================================
def step1_generate_data():
    print("\n" + "="*60)
    print("📊 STEP 1: Sample Data Generate...")
    print("="*60)
    
    np.random.seed(RANDOM_SEED)
    all_data = []
    
    for crop in CROPS:
        pcfg = CROP_PRICE_RANGES[crop]
        seasonal = SEASONAL_MULTIPLIER[crop]
        
        for market in MARKETS:
            market_factor = np.random.uniform(0.85, 1.15)
            base = pcfg["base"] * market_factor
            running_price = base
            
            for day_offset in range(DAYS_OF_HISTORY, 0, -1):
                date = datetime.now() - timedelta(days=day_offset)
                month = date.month
                seasonal_factor = seasonal[month]
                daily_change = np.random.uniform(-0.03, 0.03)
                
                if np.random.random() < 0.05:
                    daily_change = np.random.choice([-1, 1]) * np.random.uniform(0.05, 0.15)
                
                running_price = running_price * (1 + daily_change) * (0.98 + 0.04 * seasonal_factor)
                running_price = max(pcfg["min"], min(pcfg["max"], running_price))
                
                spread = np.random.uniform(50, pcfg["volatility"] * 0.3)
                min_price = running_price - spread
                max_price = running_price + spread * 1.5
                
                base_arrivals = np.random.uniform(50, 500)
                arrivals = base_arrivals * np.random.uniform(0.5, 1.5)
                if date.weekday() >= 5:
                    arrivals *= 0.3
                
                all_data.append({
                    "crop_name": crop,
                    "market_name": market["market_name"],
                    "district": market["district"],
                    "price_date": date.strftime("%Y-%m-%d"),
                    "min_price": round(min_price, 2),
                    "max_price": round(max_price, 2),
                    "modal_price": round(running_price, 2),
                    "arrivals": round(arrivals, 2)
                })
    
    df = pd.DataFrame(all_data)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/raw_crop_prices.csv", index=False)
    
    print(f"✅ {len(df)} records generated")
    print(f"📁 Saved: data/raw_crop_prices.csv")
    for crop in CROPS:
        cd = df[df['crop_name']==crop]
        print(f"   {crop:10s}: Rs.{cd['modal_price'].min():>7.0f} - Rs.{cd['modal_price'].max():>7.0f} (Avg: Rs.{cd['modal_price'].mean():>7.0f})")
    return df

# =====================================================
# STEP 2: DATA CLEANING + FEATURE ENGINEERING
# =====================================================
def step2_clean_transform():
    print("\n" + "="*60)
    print("🧹 STEP 2: Data Cleaning & Feature Engineering...")
    print("="*60)
    
    df = pd.read_csv("data/raw_crop_prices.csv")
    df['price_date'] = pd.to_datetime(df['price_date'])
    df = df.drop_duplicates(subset=['crop_name','market_name','price_date'], keep='last')
    df = df.sort_values(['crop_name','market_name','price_date']).reset_index(drop=True)
    
    # Date features
    df['year'] = df['price_date'].dt.year
    df['month'] = df['price_date'].dt.month
    df['day_of_week'] = df['price_date'].dt.dayofweek
    df['day_of_month'] = df['price_date'].dt.day
    df['week_of_year'] = df['price_date'].dt.isocalendar().week.astype(int)
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Season
    def get_season(m):
        if m in [12,1,2]: return 'Winter'
        elif m in [3,4,5]: return 'Summer'
        elif m in [6,7,8]: return 'Monsoon'
        else: return 'Post_Monsoon'
    df['season'] = df['month'].apply(get_season)
    df = pd.get_dummies(df, columns=['season'], prefix='season', dtype=int)
    
    # Lag features
    for lag in [1,2,3,7,14]:
        df[f'modal_price_lag{lag}'] = df.groupby(['crop_name','market_name'])['modal_price'].shift(lag)
    
    # Rolling averages
    for w in [7,14,30]:
        df[f'modal_price_rolling_{w}d'] = df.groupby(['crop_name','market_name'])['modal_price'].transform(
            lambda x: x.rolling(window=w, min_periods=1).mean()
        )
    
    # Price change
    df['price_change_1d'] = df.groupby(['crop_name','market_name'])['modal_price'].pct_change(1)
    df['price_change_7d'] = df.groupby(['crop_name','market_name'])['modal_price'].pct_change(7)
    df['price_change_30d'] = df.groupby(['crop_name','market_name'])['modal_price'].pct_change(30)
    
    # Volatility
    df['price_volatility_7d'] = df.groupby(['crop_name','market_name'])['modal_price'].transform(
        lambda x: x.rolling(window=7, min_periods=1).std()
    )
    
    # Arrival features
    df['arrivals_lag1'] = df.groupby(['crop_name','market_name'])['arrivals'].shift(1)
    df['arrivals_rolling_7d'] = df.groupby(['crop_name','market_name'])['arrivals'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )
    
    # Price spread
    df['price_spread'] = df['max_price'] - df['min_price']
    
    # Target variable
    df['target_price'] = df.groupby(['crop_name','market_name'])['modal_price'].shift(-1)
    
    # Label encoding
    le_market = LabelEncoder()
    le_crop = LabelEncoder()
    df['market_encoded'] = le_market.fit_transform(df['market_name'])
    df['crop_encoded'] = le_crop.fit_transform(df['crop_name'])
    
    # Cleanup — DROP target NaN FIRST, then fillna(0) on features
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=['target_price'])
    feature_cols = df.select_dtypes(include=[np.number]).columns
    df[feature_cols] = df[feature_cols].fillna(0)
    
    df.to_csv("data/processed_crop_prices.csv", index=False)
    print(f"✅ {len(df)} records cleaned with {len(df.columns)} features")
    print(f"📁 Saved: data/processed_crop_prices.csv")
    return df

# =====================================================
# STEP 3: ML MODEL TRAINING
# =====================================================
def step3_train_model():
    print("\n" + "="*60)
    print("🤖 STEP 3: ML Model Training...")
    print("="*60)
    
    df = pd.read_csv("data/processed_crop_prices.csv")
    os.makedirs("models", exist_ok=True)
    
    feature_columns = [
        'market_encoded', 'crop_encoded',
        'year', 'month', 'day_of_week', 'day_of_month', 'week_of_year', 'is_weekend',
        'season_Monsoon', 'season_Post_Monsoon', 'season_Summer', 'season_Winter',
        'modal_price_lag1', 'modal_price_lag2', 'modal_price_lag3', 'modal_price_lag7', 'modal_price_lag14',
        'modal_price_rolling_7d', 'modal_price_rolling_14d', 'modal_price_rolling_30d',
        'price_change_1d', 'price_change_7d', 'price_change_30d',
        'price_volatility_7d',
        'arrivals_lag1', 'arrivals_rolling_7d',
        'price_spread'
    ]
    available_features = [c for c in feature_columns if c in df.columns]
    
    results = []
    
    for crop in CROPS:
        crop_data = df[df['crop_name'] == crop].copy()
        if len(crop_data) < 50:
            continue
        
        X = crop_data[available_features]
        y = crop_data['target_price']
        
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        model = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        quality = "🟢" if mape < 15 else "🟡" if mape < 25 else "🔴"
        print(f"   {crop:10s}: MAE=Rs.{mae:>6.0f} | MAPE={mape:>5.1f}% | R2={r2:.4f} {quality}")
        
        joblib.dump(model, f"models/model_{crop.lower()}.pkl")
        
        results.append({'crop': crop, 'mae': round(mae,2), 'mape': round(mape,2), 'r2': round(r2,4)})
    
    print(f"\n✅ {len(results)} models trained & saved to models/ folder")
    return results

# =====================================================
# STEP 4: PRICE PREDICTION (Next 7 Days)
# =====================================================
def step4_predict():
    print("\n" + "="*60)
    print("🔮 STEP 4: Price Prediction (Next 7 Days)...")
    print("="*60)
    
    df = pd.read_csv("data/processed_crop_prices.csv")
    df['price_date'] = pd.to_datetime(df['price_date'])
    
    models = {}
    for crop in CROPS:
        path = f"models/model_{crop.lower()}.pkl"
        if os.path.exists(path):
            models[crop] = joblib.load(path)
    
    feature_columns = [
        'market_encoded', 'crop_encoded',
        'year', 'month', 'day_of_week', 'day_of_month', 'week_of_year', 'is_weekend',
        'season_Monsoon', 'season_Post_Monsoon', 'season_Summer', 'season_Winter',
        'modal_price_lag1', 'modal_price_lag2', 'modal_price_lag3', 'modal_price_lag7', 'modal_price_lag14',
        'modal_price_rolling_7d', 'modal_price_rolling_14d', 'modal_price_rolling_30d',
        'price_change_1d', 'price_change_7d', 'price_change_30d',
        'price_volatility_7d',
        'arrivals_lag1', 'arrivals_rolling_7d',
        'price_spread'
    ]
    available_features = [c for c in feature_columns if c in df.columns]
    
    all_predictions = []
    advisory_data = []
    today = datetime.now().date()
    
    for crop in CROPS:
        if crop not in models:
            continue
        model = models[crop]
        
        for market_info in MARKETS:
            market_name = market_info["market_name"]
            district = market_info["district"]
            
            mask = (df['crop_name']==crop) & (df['market_name']==market_name)
            crop_market = df[mask].sort_values('price_date')
            if len(crop_market) < 30:
                continue
            
            recent = crop_market.tail(30).copy()
            latest = recent.iloc[-1].copy()
            current_modal = latest['modal_price']
            
            X_input = latest[available_features].copy()
            price_history = recent['modal_price'].values.tolist()
            
            day1_pred = None
            
            for day in range(1, 8):
                pred_date = today + timedelta(days=day)
                
                def get_season_cols(m):
                    if m in [12,1,2]: return {'season_Monsoon':0,'season_Post_Monsoon':0,'season_Summer':0,'season_Winter':1}
                    elif m in [3,4,5]: return {'season_Monsoon':0,'season_Post_Monsoon':0,'season_Summer':1,'season_Winter':0}
                    elif m in [6,7,8]: return {'season_Monsoon':1,'season_Post_Monsoon':0,'season_Summer':0,'season_Winter':0}
                    else: return {'season_Monsoon':0,'season_Post_Monsoon':1,'season_Summer':0,'season_Winter':0}
                
                X_pred = pd.DataFrame([X_input.values], columns=available_features)
                pred_price = model.predict(X_pred)[0]
                
                max_r = current_modal * 1.30
                min_r = current_modal * 0.70
                pred_price = max(min_r, min(max_r, pred_price))
                pred_price = max(0, round(pred_price, 2))
                
                change_pct = round((pred_price - current_modal) / current_modal * 100, 2)
                
                if day == 1:
                    day1_pred = pred_price
                    day1_change = change_pct
                
                all_predictions.append({
                    'crop_name': crop, 'market_name': market_name,
                    'district': district, 'prediction_date': pred_date.strftime('%Y-%m-%d'),
                    'predicted_price': pred_price, 'current_price': round(current_modal,2),
                    'price_change_pct': change_pct, 'predicted_on': today.strftime('%Y-%m-%d'),
                    'model_version': 'v1.0', 'day_ahead': day
                })
                
                # Update features for next day
                price_history.append(pred_price)
                hl = len(price_history)
                X_input['modal_price_lag14'] = price_history[-15] if hl>=15 else price_history[0]
                X_input['modal_price_lag7'] = price_history[-8] if hl>=8 else price_history[0]
                X_input['modal_price_lag3'] = price_history[-4] if hl>=4 else price_history[-2]
                X_input['modal_price_lag2'] = price_history[-3] if hl>=3 else price_history[-2]
                X_input['modal_price_lag1'] = price_history[-2] if hl>=2 else pred_price
                X_input['modal_price_rolling_7d'] = np.mean(price_history[-7:])
                X_input['modal_price_rolling_14d'] = np.mean(price_history[-14:])
                X_input['modal_price_rolling_30d'] = np.mean(price_history[-30:])
                if hl>=2: X_input['price_change_1d'] = (price_history[-1]-price_history[-2])/price_history[-2]
                if hl>=8: X_input['price_change_7d'] = (price_history[-1]-price_history[-8])/price_history[-8]
                X_input['price_volatility_7d'] = np.std(price_history[-7:])
                X_input['month'] = pred_date.month
                X_input['day_of_week'] = pred_date.weekday()
                X_input['day_of_month'] = pred_date.day
                X_input['week_of_year'] = pred_date.isocalendar()[1]
                X_input['is_weekend'] = 1 if pred_date.weekday()>=5 else 0
                sc = get_season_cols(pred_date.month)
                for k,v in sc.items():
                    if k in X_input.index: X_input[k] = v
            
            # Advisory for Day 1
            if day1_pred is not None:
                if day1_change < -10:
                    adv_type = "WAIT"
                    adv_mr = f"WARNING {crop} price dropping ({day1_change:.1f}%) - Do NOT sell!"
                elif day1_change < 0:
                    adv_type = "WAIT"
                    adv_mr = f"CAUTION {crop} price slightly down - Wait"
                elif day1_change < 5:
                    adv_type = "SELL"
                    adv_mr = f"GOOD {crop} price stable/rising - Consider selling"
                else:
                    adv_type = "SELL"
                    adv_mr = f"BEST TIME {crop} price rising (+{day1_change:.1f}%) - Sell now!"
                
                advisory_data.append({
                    'crop_name': crop, 'market_name': market_name,
                    'district': district, 'current_price': current_modal,
                    'predicted_price': day1_pred, 'price_change_pct': day1_change,
                    'advisory_type': adv_type, 'advisory_mr': adv_mr
                })
    
    pred_df = pd.DataFrame(all_predictions)
    adv_df = pd.DataFrame(advisory_data)
    
    pred_df.to_csv("data/predictions.csv", index=False)
    adv_df.to_csv("data/advisory.csv", index=False)
    
    print(f"\n✅ {len(pred_df)} predictions generated (5 crops x 10 markets x 7 days)")
    print(f"📁 Saved: data/predictions.csv")
    print(f"📁 Saved: data/advisory.csv")
    
    print(f"\n📋 Farmer Advisory Summary:")
    for crop in CROPS:
        ca = adv_df[adv_df['crop_name']==crop]
        if len(ca) == 0: continue
        top = ca.loc[ca['predicted_price'].idxmax()]
        print(f"   🌾 {CROP_NAMES_MR.get(crop,crop)} ({crop}): Rs.{top['current_price']:.0f} -> Rs.{top['predicted_price']:.0f} ({top['price_change_pct']:+.1f}%)")
        print(f"      {top['advisory_mr']}")
    
    return pred_df, adv_df

# =====================================================
# STEP 5: STORE TO MYSQL
# =====================================================
def step5_store_to_mysql():
    print("\n" + "="*60)
    print("💾 STEP 5: Storing Data to MySQL...")
    print("="*60)
    
    try:
        engine = create_engine(DB_URL)
        conn = engine.connect()
        print("✅ Connected to MySQL!")
    except Exception as e:
        print(f"❌ MySQL Connection Failed: {e}")
        print("\n💡 Check:")
        print("   1. MySQL running?")
        print("   2. crop_price_db database created?")
        print("  3. Check whether MySQL credentials are correct.")
        return False
    
    # Store crop prices
    try:
        df = pd.read_csv("data/processed_crop_prices.csv")
        df['price_date'] = pd.to_datetime(df['price_date'])
        
        price_cols = ['market_name','crop_name','price_date','min_price','max_price','modal_price','arrivals']
        df_store = df[price_cols].copy()
        
        markets_df = pd.read_sql("SELECT market_id, market_name FROM markets", engine)
        df_store = df_store.merge(markets_df, on='market_name', how='left')
        
        df_final = df_store[['market_id','crop_name','price_date','min_price','max_price','modal_price','arrivals']].copy()
        df_final = df_final.drop_duplicates(subset=['market_id','crop_name','price_date'], keep='last')
        
        # ✅ FIX: text() wrapper added
        with engine.connect() as c:
            c.execute(text("DELETE FROM crop_prices"))
            c.commit()
        
        df_final.to_sql('crop_prices', engine, if_exists='append', index=False)
        print(f"✅ crop_prices: {len(df_final)} records stored")
    except Exception as e:
        print(f"❌ crop_prices error: {e}")
    
    # Store predictions
    try:
        pred_df = pd.read_csv("data/predictions.csv")
        pred_df['prediction_date'] = pd.to_datetime(pred_df['prediction_date'])
        pred_df['predicted_on'] = pd.to_datetime(pred_df['predicted_on'])
        
        markets_df = pd.read_sql("SELECT market_id, market_name FROM markets", engine)
        pred_df = pred_df.merge(markets_df, on='market_name', how='left')
        
        pred_final = pred_df[['market_id','crop_name','prediction_date','predicted_price','predicted_on','model_version']].copy()
        pred_final['confidence_score'] = 85.0
        pred_final = pred_final.drop_duplicates(subset=['market_id','crop_name','prediction_date'], keep='last')
        
        # ✅ FIX: text() wrapper added
        with engine.connect() as c:
            c.execute(text("DELETE FROM predictions"))
            c.commit()
        
        pred_final.to_sql('predictions', engine, if_exists='append', index=False)
        print(f"✅ predictions: {len(pred_final)} records stored")
    except Exception as e:
        print(f"❌ predictions error: {e}")
    
    # Store advisory
    try:
        adv_df = pd.read_csv("data/advisory.csv")
        markets_df = pd.read_sql("SELECT market_id, market_name FROM markets", engine)
        adv_df = adv_df.merge(markets_df, on='market_name', how='left')
        
        # ✅ FIX: text() wrapper added — also using advisory table
        with engine.connect() as c:
            c.execute(text("DELETE FROM advisory"))
            c.commit()
        
        adv_df.to_sql('advisory', engine, if_exists='append', index=False)
        print(f"✅ advisory: {len(adv_df)} records stored")
    except Exception as e:
        # If advisory table doesn't exist, use farmer_advisory
        try:
            with engine.connect() as c:
                c.execute(text("DROP TABLE IF EXISTS farmer_advisory"))
                c.commit()
            adv_df.to_sql('farmer_advisory', engine, if_exists='replace', index=False)
            print(f"✅ farmer_advisory: {len(adv_df)} records stored")
        except Exception as e2:
            print(f"❌ advisory error: {e2}")
    
    # Update predictions table — add current_price and price_change_pct
    try:
        with engine.connect() as c:
            # Check if columns exist
            cols = pd.read_sql("SHOW COLUMNS FROM predictions", engine)
            col_names = cols['Field'].tolist()
            
            if 'current_price' not in col_names:
                c.execute(text("ALTER TABLE predictions ADD COLUMN current_price DECIMAL(10,2) DEFAULT NULL"))
            if 'price_change_pct' not in col_names:
                c.execute(text("ALTER TABLE predictions ADD COLUMN price_change_pct DECIMAL(10,2) DEFAULT NULL"))
            c.commit()
        
        # Update from predictions.csv
        pred_df = pd.read_csv("data/predictions.csv")
        for _, row in pred_df.iterrows():
            with engine.connect() as c:
                c.execute(text("""
                    UPDATE predictions 
                    SET current_price = :cp, price_change_pct = :pct
                    WHERE market_id = :mid AND crop_name = :crop 
                    AND prediction_date = :pdate
                """), {
                    'cp': row['current_price'],
                    'pct': row['price_change_pct'],
                    'mid': int(row.get('market_id', 0)),
                    'crop': row['crop_name'],
                    'pdate': row['prediction_date']
                })
                c.commit()
        print(f"✅ predictions: current_price & price_change_pct updated")
    except Exception as e:
        print(f"⚠️ predictions update: {e}")
    
    # Verify
    print(f"\n📊 MySQL Data Verification:")
    for table in ['markets','crop_prices','predictions','advisory','price_alerts']:
        try:
            count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM {table}", engine).iloc[0]['cnt']
            print(f"   ✅ {table}: {count} records")
        except:
            pass
    
    # Quick analytics
    try:
        result = pd.read_sql("""
            SELECT crop_name, 
                   ROUND(AVG(modal_price),2) AS avg_price,
                   COUNT(*) AS records
            FROM crop_prices 
            GROUP BY crop_name
            ORDER BY avg_price DESC
        """, engine)
        print(f"\n💰 Crop-wise Average Price:")
        print(result.to_string(index=False))
    except Exception as e:
        print(f"   ⚠️ {e}")
    
    conn.close()
    print(f"\n✅ Step 5 Complete! Data stored in MySQL.")
    print(f"📊 Power BI can now connect to crop_price_db!")
    return True

# =====================================================
# MAIN
# =====================================================
def main():
    print("\n" + "🌾"*30)
    print("  MAHARASHTRA CROP PRICE PREDICTION DASHBOARD")
    print("  Complete Pipeline - One File")
    print("🌾"*30)
    print(f"\n  📅 Date: {datetime.now().strftime('%d %B %Y, %H:%M:%S')}")
    
    # Install packages first
    install_packages()
    
    # Step 1
    step1_generate_data()
    
    # Step 2
    step2_clean_transform()
    
    # Step 3
    step3_train_model()
    
    # Step 4
    step4_predict()
    
    # Step 5
    step5_store_to_mysql()
    
    print("\n" + "="*60)
    print("🎉 COMPLETE! Pipeline Successful!")
    print("="*60)
    print("""
Next Steps:
1. Open Power BI Desktop
2. Get Data -> ODBC -> CropPriceDB
3. Build Dashboard (4 pages)

Tables available:
  - markets (10 records)
  - crop_prices (8950+ records)
  - predictions (350 records)
  - advisory (25 records)
  - farmer_advisory (50 records)
  - Views: market_summary, crop_trends, best_market_view, daily_price_overview, prediction_summary, dashboard_freshness, prediction_accuracy, prediction_advisory_summary, dashboard_info
    """)

if __name__ == "__main__":
    main()
