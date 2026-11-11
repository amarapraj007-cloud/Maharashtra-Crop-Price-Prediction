"""
====================================================
🌐 AGMARKNET Real Data Fetcher
====================================================
हा code AGMARKNET (Government of India) वरून
real crop price data fetch करतो.

2 Methods:
  Method 1: API (if available)
  Method 2: Web Scraping (Selenium)

Integration: crop_pipeline.py मध्ये Step 1 replace करा
====================================================
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================
# CONFIGURATION
# =====================================================
CROPS_AGMARKNET = {
    "Onion": "Onion",
    "Tomato": "Tomato", 
    "Soybean": "Soyabean",
    "Cotton": "Cotton",
    "Gram": "Gram"
}

MARKETS_AGMARKNET = {
    "Lasalgaon": {"district": "Nashik", "state": "Maharashtra"},
    "Pimpalgaon": {"district": "Nashik", "state": "Maharashtra"},
    "Nanded": {"district": "Nanded", "state": "Maharashtra"},
    "Latur": {"district": "Latur", "state": "Maharashtra"},
    "Jalgaon": {"district": "Jalgaon", "state": "Maharashtra"},
    "Aurangabad": {"district": "Aurangabad", "state": "Maharashtra"},
    "Solapur": {"district": "Solapur", "state": "Maharashtra"},
    "Amravati": {"district": "Amravati", "state": "Maharashtra"},
    "Dhule": {"district": "Dhule", "state": "Maharashtra"},
    "Kolhapur": {"district": "Kolhapur", "state": "Maharashtra"},
}

AGMARKNET_API_URL = "https://agmarknet.gov.in/api/agmarknet/price"
AGMARKNET_WEB_URL = "https://agmarknet.gov.in/SearchCmmMkt.aspx"

# =====================================================
# METHOD 1: API BASED FETCHING (Preferred)
# =====================================================
def fetch_via_api(crop_name, market_name, district, state, days=180):
    """
    AGMARKNET API वरून data fetch करा
    
    Note: AGMARKNET API endpoint may change.
    Check: https://agmarknet.gov.in for latest API docs
    """
    
    to_date = datetime.now().strftime('%d-%m-%Y')
    from_date = (datetime.now() - timedelta(days=days)).strftime('%d-%m-%Y')
    
    params = {
        'state': state,
        'district': district,
        'market': market_name,
        'commodity': CROPS_AGMARKNET.get(crop_name, crop_name),
        'from_date': from_date,
        'to_date': to_date,
        'format': 'json'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://agmarknet.gov.in/'
    }
    
    try:
        response = requests.get(AGMARKNET_API_URL, params=params, 
                               headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            if not records:
                logger.warning(f"No data for {crop_name} @ {market_name}")
                return None
            
            df = pd.DataFrame(records)
            return df
        else:
            logger.error(f"API Error {response.status_code}: {crop_name} @ {market_name}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout: {crop_name} @ {market_name}")
        return None
    except Exception as e:
        logger.error(f"API Error: {e}")
        return None


# =====================================================
# METHOD 2: WEB SCRAPING (Fallback)
# =====================================================
def fetch_via_scraping(crop_name, market_name, district, state, days=30):
    """
    AGMARKNET website वरून Selenium ने data scrape करा
    
    Requirements: pip install selenium
    Also need: ChromeDriver installed
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select, WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        logger.error("Selenium not installed! Run: pip install selenium")
        return None
    
    driver = None
    try:
        # Headless Chrome (no browser window)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.get(AGMARKNET_WEB_URL)
        time.sleep(3)
        
        # Select State
        state_dd = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'ddlState'))
        ))
        state_dd.select_by_visible_text(state)
        time.sleep(2)
        
        # Select District
        district_dd = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'ddlDistrict'))
        ))
        district_dd.select_by_visible_text(district)
        time.sleep(2)
        
        # Select Market
        market_dd = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'ddlMarket'))
        ))
        market_dd.select_by_visible_text(market_name)
        time.sleep(2)
        
        # Select Commodity
        commodity_dd = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'ddlCommodity'))
        ))
        commodity_dd.select_by_visible_text(CROPS_AGMARKNET.get(crop_name, crop_name))
        time.sleep(2)
        
        # Set dates
        from_date = (datetime.now() - timedelta(days=days)).strftime('%d/%m/%Y')
        to_date = datetime.now().strftime('%d/%m/%Y')
        
        from_input = driver.find_element(By.ID, 'txtDateFrom')
        from_input.clear()
        from_input.send_keys(from_date)
        
        to_input = driver.find_element(By.ID, 'txtDateTo')
        to_input.clear()
        to_input.send_keys(to_date)
        time.sleep(1)
        
        # Click Search
        search_btn = driver.find_element(By.ID, 'btnGo')
        search_btn.click()
        time.sleep(5)
        
        # Read table
        table = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, 'cphBody_gridRecords'))
        )
        rows = table.find_elements(By.TAG_NAME, 'tr')
        
        data = []
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 7:
                try:
                    data.append({
                        'crop_name': crop_name,
                        'market_name': market_name,
                        'district': district,
                        'price_date': cells[0].text.strip(),
                        'min_price': float(cells[3].text.replace(',', '')),
                        'max_price': float(cells[4].text.replace(',', '')),
                        'modal_price': float(cells[5].text.replace(',', '')),
                        'arrivals': float(cells[6].text.replace(',', ''))
                    })
                except (ValueError, IndexError):
                    continue
        
        if data:
            df = pd.DataFrame(data)
            logger.info(f"  Scraped {len(df)} records: {crop_name} @ {market_name}")
            return df
        else:
            logger.warning(f"No data scraped: {crop_name} @ {market_name}")
            return None
            
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return None
    finally:
        if driver:
            driver.quit()


# =====================================================
# METHOD 3: AGMARKNET OPEN DATA PORTAL
# =====================================================
def fetch_via_opendata(crop_name, market_name, days=180):
    """
    AGMARKNET Open Data Portal वरून data fetch करा
    URL: https://data.gov.in/catalog/daily-wholesale-price-major-agricultural-commodities
    
    This uses the data.gov.in API which provides bulk download
    """
    
    # data.gov.in API key (free registration required)
    API_KEY = "YOUR_DATA_GOV_IN_API_KEY"
    
    url = f"https://api.data.gov.in/resource/9ef84268-d588-4ada-ae8e-4b9f6c7be4d6"
    
    params = {
        'api-key': API_KEY,
        'format': 'json',
        'filters[state]': 'Maharashtra',
        'filters[market]': market_name,
        'filters[commodity]': CROPS_AGMARKNET.get(crop_name, crop_name),
        'limit': days
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            if records:
                return pd.DataFrame(records)
    except Exception as e:
        logger.error(f"OpenData error: {e}")
    
    return None


# =====================================================
# MAIN: FETCH ALL CROPS × MARKETS
# =====================================================
def fetch_all_real_data(method='api'):
    """
    सर्व 5 crops × 10 markets साठी data fetch करा
    
    Args:
        method: 'api' | 'scraping' | 'opendata'
    
    Returns:
        DataFrame with all price records
    """
    
    all_data = []
    total_calls = len(CROPS_AGMARKNET) * len(MARKETS_AGMARKNET)
    current = 0
    
    logger.info(f"🌐 Fetching real AGMARKNET data ({total_calls} combinations)...")
    
    for crop_name in CROPS_AGMARKNET:
        for market_name, info in MARKETS_AGMARKNET.items():
            current += 1
            district = info['district']
            state = info['state']
            
            logger.info(f"  [{current}/{total_calls}] {crop_name} @ {market_name}...")
            
            if method == 'api':
                df = fetch_via_api(crop_name, market_name, district, state)
            elif method == 'scraping':
                df = fetch_via_scraping(crop_name, market_name, district, state)
            elif method == 'opendata':
                df = fetch_via_opendata(crop_name, market_name)
            else:
                df = None
            
            if df is not None and len(df) > 0:
                # Standardize column names
                df['crop_name'] = crop_name
                df['market_name'] = market_name
                df['district'] = district
                all_data.append(df)
            
            # Rate limiting - don't overload the server
            time.sleep(2)
    
    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        logger.info(f"✅ Fetched {len(result)} total records from AGMARKNET")
        return result
    else:
        logger.error("❌ No data fetched from AGMARKNET!")
        return None


# =====================================================
# INTEGRATION WITH PIPELINE
# =====================================================
def step1_fetch_real_data():
    """
    crop_pipeline.py च्या step1_generate_data() replace करा
    हे function ने real AGMARKNET data fetch करा
    """
    
    print("\n" + "="*60)
    print("🌐 STEP 1: Fetching Real AGMARKNET Data...")
    print("="*60)
    
    # Try API first, then scraping as fallback
    df = fetch_all_real_data(method='api')
    
    if df is None:
        print("⚠️ API failed, trying web scraping...")
        df = fetch_all_real_data(method='scraping')
    
    if df is None:
        print("⚠️ Scraping also failed, using sample data as fallback...")
        # Fallback to sample data generation
        from crop_pipeline import step1_generate_data
        df = step1_generate_data()
        return df
    
    # Clean the data
    import os
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/raw_crop_prices.csv", index=False)
    
    print(f"✅ {len(df)} records fetched from AGMARKNET")
    return df


# =====================================================
# TESTING
# =====================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌐 AGMARKNET Real Data Fetcher")
    print("="*60)
    print()
    print("Methods available:")
    print("  1. API (Fast, preferred)")
    print("  2. Web Scraping (Selenium, fallback)")
    print("  3. Open Data Portal (data.gov.in)")
    print()
    print("⚠️ Note: AGMARKNET API endpoints may change.")
    print("   Check https://agmarknet.gov.in for latest API docs")
    print()
    
    # Quick test - fetch one crop + one market
    print("Quick Test: Fetching Onion @ Lasalgaon...")
    df = fetch_via_api("Onion", "Lasalgaon", "Nashik", "Maharashtra", days=7)
    if df is not None:
        print(f"✅ Got {len(df)} records")
        print(df.head())
    else:
        print("❌ API not available. Try scraping method.")
