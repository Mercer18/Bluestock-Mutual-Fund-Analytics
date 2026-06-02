# Bluestock Mutual Fund Analytics Platform

An end-to-end data engineering, ETL, database storage, and analytical query platform to process, clean, and analyze Indian mutual fund data.

---

## Folder Structure

```text
Capstone/
├── data/
│   ├── raw/                 # Ingested raw datasets (including live NAVs from API)
│   ├── processed/           # Transformed & cleaned datasets
│   └── db/                  # Relational SQLite database (bluestock_mf.db)
├── notebooks/
│   ├── 01_data_ingestion.ipynb   # Day 1: Loads and inspects CSV metadata & validates AMFI codes
│   └── 02_database_load.ipynb    # Day 2: Loads cleaned CSVs to SQLite & executes 10 test SQL queries
├── scripts/
│   └── live_nav_fetch.py    # Day 1: Python script to fetch live NAV values from mfapi.in API
├── sql/
│   ├── schema.sql           # Day 2: Star Schema definition (dimensions, facts, and indices)
│   └── queries.sql          # Day 2: The 10 analytical SQL queries
├── reports/
│   └── data_dictionary.md   # Day 2: Database schema reference documentation
└── requirements.txt         # Project package dependencies
```

---

## Setup & Execution Guide

### 1. Environment Setup
Create and activate your Python virtual environment, then install all project requirements:
```bash
# Verify pip is pointed to your .venv and install dependencies
pip install -r requirements.txt
```

### 2. Live NAV Fetching (ETL Ingestion)
To fetch live and historical NAV data for the key mutual fund schemes (SBI, HDFC, ICICI, Axis, Nippon, Kotak) from the public REST API:
```bash
python scripts/live_nav_fetch.py
```
This script includes a rate-limiting delay and retry mechanism to handle public API rate limits (Bad Gateway errors).

### 3. Data Cleaning, Star Schema Creation & Database Load
* The `01_data_ingestion.ipynb` notebook reads the raw files and validates that every code in the Fund Master exists in the NAV history.
* The `02_database_load.ipynb` notebook reads the SQL DDL from `sql/schema.sql` to initialize the database tables, loads the cleaned datasets from `data/processed/` using SQLAlchemy, and runs the 10 analytical SQL queries.

To run the notebooks programmatically from command line:
```bash
# Execute Data Ingestion
jupyter nbconvert --to notebook --execute --inplace notebooks/01_data_ingestion.ipynb

# Execute Database Load & SQL Queries
jupyter nbconvert --to notebook --execute --inplace notebooks/02_database_load.ipynb
```

---

## Key SQL Queries Implemented
The database is structured as a **Star Schema** optimized for high-performance financial reports. Some sample analytical queries implemented include:
* Top 5 fund houses by total AUM in the latest quarter.
* Average NAV per month for HDFC Top 100.
* Year-on-Year Growth of monthly SIP inflows.
* Geographical transaction volumes and amounts.
* Low expense ratio funds (< 1%).
* Industry portfolio sector concentrations.
* 30-Day moving averages of Net Asset Values.
