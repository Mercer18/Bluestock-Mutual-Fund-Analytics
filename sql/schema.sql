-- schema.sql
-- Star Schema DDL for Bluestock Mutual Fund Analytics Platform

-- 1. Dimension: Fund Master
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code TEXT PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date TEXT,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- 2. Dimension: Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    is_weekday INTEGER NOT NULL -- Boolean: 0 or 1
);

-- 3. Fact Table: Daily NAV History
CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code TEXT,
    date TEXT,
    nav REAL NOT NULL,
    daily_return_pct REAL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

-- 4. Fact Table: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    amfi_code TEXT NOT NULL,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL, -- SIP, Lumpsum, Redemption
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

-- 5. Fact Table: Scheme Performance Metrics
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code TEXT PRIMARY KEY,
    as_of_date TEXT,
    return_1yr REAL,
    return_3yr REAL,
    return_5yr REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe REAL,
    sortino REAL,
    std_dev_ann_pct REAL,
    max_dd REAL,
    morningstar_rating INTEGER,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- 6. Fact Table: Fund Portfolio Holdings
CREATE TABLE IF NOT EXISTS fact_portfolio (
    portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT NOT NULL,
    stock_symbol TEXT NOT NULL,
    weight_pct REAL NOT NULL,
    sector TEXT,
    date TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- 7. Fact Table: Fund House AUM Trends
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house TEXT NOT NULL,
    date TEXT NOT NULL,
    aum_crore REAL NOT NULL,
    num_schemes INTEGER,
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

-- 8. Fact Table: SIP Inflows Industry-Wide
CREATE TABLE IF NOT EXISTS fact_sip_industry (
    month TEXT PRIMARY KEY,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

-- Indices for performance tuning
CREATE INDEX IF NOT EXISTS idx_nav_amfi_date ON fact_nav(amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_tx_amfi_date ON fact_transactions(amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_tx_investor ON fact_transactions(investor_id);
