"""
live_nav_fetch.py
Day 1 Capstone Project - Live Mutual Fund NAV Ingestion

This script connects to the AMFI open REST API (mfapi.in) to ingest daily historical Net Asset Value (NAV) 
records for selected target schemes, applying retry backoffs and rate limiting to avoid server connection limits.
"""

import os
import requests
import pandas as pd
import time

# List of scheme codes to fetch
schemes = {
    "125497": "HDFC_Top_100_Direct",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip"
}

# Directories
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_data_dir = os.path.join(base_dir, "data", "raw")
os.makedirs(raw_data_dir, exist_ok=True)

def fetch_and_save_nav(scheme_code, name, retries=3, delay=3):
    """
    Fetches daily NAV records for a given AMFI scheme code and saves them to a CSV file.
    
    Parameters:
    - scheme_code (str): The unique AMFI identifier for the mutual fund scheme.
    - name (str): Fallback human-readable scheme name.
    - retries (int): Maximum number of retry attempts in case of API failure.
    - delay (int): Time gap in seconds between retries.
    
    Returns:
    - bool: True if the ingestion succeeded, False otherwise.
    """
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    for attempt in range(1, retries + 1):
        print(f"Fetching NAV for {name} (Code: {scheme_code}), Attempt {attempt}/{retries}...")
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 502:
                print(f"Bad Gateway (502) on attempt {attempt}. Retrying after {delay} seconds...")
                time.sleep(delay)
                continue
            response.raise_for_status()
            data = response.json()
            
            # Extract meta and data
            meta = data.get("meta", {})
            nav_list = data.get("data", [])
            
            if not nav_list:
                print(f"No NAV data found for scheme: {scheme_code}")
                return False
            
            # Convert to DataFrame
            df = pd.DataFrame(nav_list)
            
            # Ensure correct columns exist
            df["amfi_code"] = scheme_code
            df["scheme_name"] = meta.get("scheme_name", name)
            
            # Reorder columns
            df = df[["amfi_code", "scheme_name", "date", "nav"]]
            
            # Output filepath
            output_file = os.path.join(raw_data_dir, f"raw_nav_{scheme_code}.csv")
            df.to_csv(output_file, index=False)
            print(f"Successfully saved {len(df)} records to {output_file}\n")
            return True
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                print(f"Error fetching NAV for {scheme_code} after {retries} attempts.\n")
                return False
    return False

if __name__ == "__main__":
    print("Starting Live NAV Fetching Process...\n")
    success_count = 0
    for code, name in schemes.items():
        if fetch_and_save_nav(code, name):
            success_count += 1
        # Add a sleep delay between different schemes to avoid rate limits
        time.sleep(2)
            
    print(f"Fetching complete! Successfully fetched {success_count}/{len(schemes)} schemes.")


