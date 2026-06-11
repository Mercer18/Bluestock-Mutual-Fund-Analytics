# run_pipeline.py
# Day 7 Capstone Project - Master Execution Pipeline

import os
import sys
import subprocess
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# Base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

def print_header(title):
    print("=" * 80)
    print(f" {title.upper()} ".center(80, "="))
    print("=" * 80)

def run_script(script_name):
    script_path = os.path.join(base_dir, 'scripts', script_name)
    print(f"Running script: {script_name}...")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing {script_name}:")
        print(result.stderr)
        sys.exit(1)
    else:
        print(result.stdout)
        print(f"Finished {script_name} successfully.\n")

def load_database():
    print_header("Step 2: Relational Database Initialization & Loading")
    processed_dir = os.path.join(base_dir, "data", "processed")
    db_dir = os.path.join(base_dir, "data", "db")
    db_path = os.path.join(db_dir, "bluestock_mf.db")
    schema_path = os.path.join(base_dir, "sql", "schema.sql")
    
    # Clean load
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("Deleted old database file for a clean load.")
        except Exception as e:
            print(f"Warning: could not delete old database file: {e}")
            
    # Connect and run DDL
    print("Executing schema DDL scripts...")
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    print("Schema initialized successfully.")
    
    # Load with SQLAlchemy
    print("Loading datasets into SQLite facts and dimensions...")
    engine = create_engine(f"sqlite:///{db_path}")
    
    df_fund = pd.read_csv(os.path.join(processed_dir, "01_fund_master_clean.csv"))
    df_nav = pd.read_csv(os.path.join(processed_dir, "02_nav_history_clean.csv"))
    df_aum = pd.read_csv(os.path.join(processed_dir, "03_aum_by_fund_house_clean.csv"))
    df_sip = pd.read_csv(os.path.join(processed_dir, "04_monthly_sip_inflows_clean.csv"))
    df_perf = pd.read_csv(os.path.join(processed_dir, "07_scheme_performance_clean.csv"))
    df_tx = pd.read_csv(os.path.join(processed_dir, "08_investor_transactions_clean.csv"))
    df_port = pd.read_csv(os.path.join(processed_dir, "09_portfolio_holdings_clean.csv"))
    
    # Generate Date dimension
    print("Generating Date Dimension...")
    all_dates = pd.concat([
        df_nav['date'],
        df_tx['transaction_date'],
        df_aum['date']
    ]).dropna().unique()
    
    df_date = pd.DataFrame({'date': all_dates})
    df_date['date'] = pd.to_datetime(df_date['date'])
    df_date = df_date.sort_values('date')
    df_date['year'] = df_date['date'].dt.year
    df_date['month'] = df_date['date'].dt.month
    df_date['quarter'] = df_date['date'].dt.quarter
    df_date['is_weekday'] = df_date['date'].dt.weekday.map(lambda x: 1 if x < 5 else 0)
    df_date['date'] = df_date['date'].dt.strftime('%Y-%m-%d')
    
    df_date.to_sql('dim_date', con=engine, if_exists='append', index=False)
    print(f"Loaded {len(df_date)} rows into dim_date.")
    
    # Load Fund master
    print("Loading dim_fund...")
    df_fund.to_sql('dim_fund', con=engine, if_exists='append', index=False)
    
    # Load NAV facts
    print("Loading fact_nav...")
    df_nav.to_sql('fact_nav', con=engine, if_exists='append', index=False)
    
    # Load Transaction facts
    print("Loading fact_transactions...")
    df_tx_db = df_tx.rename(columns={
        'transaction_date': 'date',
        'amount_inr': 'amount',
        'transaction_type': 'type'
    })
    df_tx_db.to_sql('fact_transactions', con=engine, if_exists='append', index=False)
    
    # Load Performance facts
    print("Loading fact_performance...")
    df_perf_db = df_perf.rename(columns={
        'return_1yr_pct': 'return_1yr',
        'return_3yr_pct': 'return_3yr',
        'return_5yr_pct': 'return_5yr',
        'sharpe_ratio': 'sharpe',
        'sortino_ratio': 'sortino',
        'max_drawdown_pct': 'max_dd'
    })
    df_perf_db['as_of_date'] = '2026-05-31'
    perf_columns = [
        'amfi_code', 'as_of_date', 'return_1yr', 'return_3yr', 'return_5yr', 
        'benchmark_3yr_pct', 'alpha', 'beta', 'sharpe', 'sortino', 
        'std_dev_ann_pct', 'max_dd', 'morningstar_rating'
    ]
    df_perf_db = df_perf_db[perf_columns]
    df_perf_db.to_sql('fact_performance', con=engine, if_exists='append', index=False)
    
    # Load Portfolio facts
    print("Loading fact_portfolio...")
    df_port_db = df_port.rename(columns={'portfolio_date': 'date'})
    port_columns = ['amfi_code', 'stock_symbol', 'weight_pct', 'sector', 'date']
    df_port_db = df_port_db[port_columns]
    df_port_db.to_sql('fact_portfolio', con=engine, if_exists='append', index=False)
    
    # Load AUM facts
    print("Loading fact_aum...")
    df_aum_db = df_aum[['fund_house', 'date', 'aum_crore', 'num_schemes']]
    df_aum_db.to_sql('fact_aum', con=engine, if_exists='append', index=False)
    
    # Load SIP facts
    print("Loading fact_sip_industry...")
    df_sip.to_sql('fact_sip_industry', con=engine, if_exists='append', index=False)
    
    conn.close()
    print("All Star Schema tables populated successfully!\n")

def main():
    print_header("Bluestock Mutual Fund Capstone Execution Pipeline")
    
    # Step 1: Live NAV Ingestion
    print_header("Step 1: Live NAV API Ingestion")
    run_script('live_nav_fetch.py')
    
    # Step 2: Database Initialization and Load
    load_database()
    
    # Step 3: Performance Scorecard Analytics
    print_header("Step 3: Performance Scorecard Calculations")
    run_script('generate_analytics.py')
    
    # Step 4: Advanced Risk & Cohort Analytics
    print_header("Step 4: Advanced Risk & Cohort Analytics")
    run_script('generate_day6_analytics.py')
    
    # Step 5: PDF Final Report Generation
    print_header("Step 5: Compiling Final PDF Report")
    run_script('generate_final_report.py')
    
    # Step 6: PowerPoint Slides Generation
    print_header("Step 6: Compiling Presentation Slides")
    run_script('generate_presentation.py')
    
    print_header("Capstone Pipeline Completed Successfully")
    print("Deliverables Generated:")
    print("1. SQLite Database: Capstone/data/db/bluestock_mf.db")
    print("2. Final PDF Report: Capstone/Final_Report.pdf (and copy in reports/)")
    print("3. Presentation Slides: Capstone/Bluestock_MF_Presentation.pptx (and copy in reports/)")
    print("4. Scorecard Output: Capstone/fund_scorecard.csv")
    print("5. Risk/Return Reports: Capstone/reports/ var_cvar_report.csv, sector_hhi_report.csv, etc.")
    print("=" * 80)

if __name__ == '__main__':
    main()
