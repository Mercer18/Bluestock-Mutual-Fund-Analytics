# Bluestock Mutual Fund Analytics - Data Dictionary

This document serves as the schema reference and data dictionary for the `bluestock_mf.db` SQLite database.

---

## 1. Table: `dim_fund` (Dimension Table)
Stores descriptive metadata for all 40 mutual fund schemes.

| Column | Data Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | TEXT | PK | Unique AMFI scheme code identifier (e.g. `125497`) |
| `fund_house` | TEXT | | Asset Management Company (AMC) name (e.g. `HDFC Mutual Fund`) |
| `scheme_name` | TEXT | | Full official scheme name |
| `category` | TEXT | | Fund class (e.g. `Equity`, `Debt`, `Hybrid`) |
| `sub_category` | TEXT | | Specific fund style (e.g. `Large Cap`, `Small Cap`, `Gilt`) |
| `plan` | TEXT | | Distribution plan (e.g. `Regular`, `Direct`) |
| `launch_date` | TEXT | | Scheme inception date (YYYY-MM-DD) |
| `benchmark` | TEXT | | Index used to compare performance (e.g. `NIFTY 100 TRI`) |
| `expense_ratio_pct` | REAL | | Annual fund management fee charged to investors (%) |
| `exit_load_pct` | REAL | | Fee charged to investors upon redemption within limit (%) |
| `min_sip_amount` | REAL | | Minimum monthly SIP amount (INR) |
| `min_lumpsum_amount` | REAL | | Minimum initial lumpsum purchase amount (INR) |
| `fund_manager` | TEXT | | Name of the primary fund manager |
| `risk_category` | TEXT | | SEBI risk category label (e.g. `Low`, `Moderate`, `High`, `Very High`) |
| `sebi_category_code` | TEXT | | SEBI category identifier code (e.g. `EC01`) |

---

## 2. Table: `dim_date` (Dimension Table)
A date dimension used to slice performance and transaction facts by temporal boundaries.

| Column | Data Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `date` | TEXT | PK | Date identifier key in string format (YYYY-MM-DD) |
| `year` | INTEGER | | Year value (e.g. `2024`) |
| `month` | INTEGER | | Month index value (1 to 12) |
| `quarter` | INTEGER | | Calendar quarter (1 to 4) |
| `is_weekday` | INTEGER | | Indicator for business day: `1` = Weekday (Mon-Fri), `0` = Weekend |

---

## 3. Table: `fact_nav` (Fact Table)
Stores daily Net Asset Value (NAV) histories for all schemes. Missing weekend and holiday records have been reindexed and forward-filled.

| Column | Data Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | TEXT | PK, FK | Reference to `dim_fund(amfi_code)` |
| `date` | TEXT | PK, FK | Reference to `dim_date(date)` |
| `nav` | REAL | | Daily closing Net Asset Value in Rupees |
| `daily_return_pct` | REAL | | Daily return percentage calculated as $(NAV_{t} - NAV_{t-1}) / NAV_{t-1}$ |

---

## 4. Table: `fact_transactions` (Fact Table)
Stores simulated investment transaction data for 5,000 retail clients.

| Column | Data Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `tx_id` | INTEGER | PK | Autoincrementing transaction unique identifier |
| `investor_id` | TEXT | | Anonymized investor ID (e.g. `INV000001`) |
| `amfi_code` | TEXT | FK | Reference to `dim_fund(amfi_code)` |
| `date` | TEXT | FK | Date of transaction, references `dim_date(date)` |
| `amount` | REAL | | Transaction amount in Indian Rupees (INR) |
| `type` | TEXT | | Purchase/Redemption type (e.g. `SIP`, `Lumpsum`, `Redemption`) |
| `state` | TEXT | | State of residence of the investor (e.g. `Maharashtra`) |
| `city` | TEXT | | City of residence of the investor |
| `city_tier` | TEXT | | AMFI classification of investor location (e.g. `T30`, `B30`) |
| `age_group` | TEXT | | Investor age bracket (e.g. `26-35`) |
| `gender` | TEXT | | Gender (e.g. `Male`, `Female`) |
| `annual_income_lakh`| REAL | | Annual household income in lakhs of Rupees |
| `payment_mode` | TEXT | | Transaction payment mechanism (e.g. `UPI`, `Net Banking`, `Mandate`) |
| `kyc_status` | TEXT | | Investor KYC compliance status (e.g. `Verified`, `Pending`) |

---

## 5. Table: `fact_performance` (Fact Table)
Stores risk-adjusted metrics and returns statistics per scheme.

| Column | Data Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | TEXT | PK, FK | Reference to `dim_fund(amfi_code)` |
| `as_of_date` | TEXT | | Evaluation cutoff date for stats calculation |
| `return_1yr` | REAL | | 1-year absolute trailing returns (%) |
| `return_3yr` | REAL | | 3-year compound annual growth rate (%) |
| `return_5yr` | REAL | | 5-year compound annual growth rate (%) |
| `benchmark_3yr_pct` | REAL | | Benchmark index 3-year CAGR (%) |
| `alpha` | REAL | | Excess returns generated above benchmark (%) |
| `beta` | REAL | | Volatility of fund relative to benchmark index (market sensitivty) |
| `sharpe` | REAL | | Risk-adjusted returns relative to risk-free rate (6.5%) |
| `sortino` | REAL | | Risk-adjusted returns relative to downside volatility |
| `std_dev_ann_pct` | REAL | | Annualized standard deviation of daily returns (%) |
| `max_dd` | REAL | | Peak-to-trough drop percentage (negative value) |
| `morningstar_rating`| INTEGER | | Standard 1-to-5 star quality rating |

---

## 6. Table: `fact_portfolio` (Fact Table)
Stores details of the underlying stock holdings for each equity mutual fund scheme.

| Column | Data Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `portfolio_id` | INTEGER | PK | Autoincrementing record identifier |
| `amfi_code` | TEXT | FK | Reference to `dim_fund(amfi_code)` |
| `stock_symbol` | TEXT | | Equity ticker symbol on NSE (e.g. `POWERGRID`) |
| `weight_pct` | REAL | | Allocation weight inside the scheme portfolio (%) |
| `sector` | TEXT | | Industry segment category (e.g. `Utilities`, `Banking`) |
| `date` | TEXT | | Portfolio composition disclosure date (YYYY-MM-DD) |

---

## 7. Table: `fact_aum` (Fact Table)
Tracks Assets Under Management (AUM) trends across the 10 largest fund houses.

| Column | Data Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `aum_id` | INTEGER | PK | Autoincrementing record identifier |
| `fund_house` | TEXT | | AMC Name |
| `date` | TEXT | FK | End of calendar quarter (references `dim_date(date)`) |
| `aum_crore` | REAL | | Total assets managed by AMC in Rs. Crores |
| `num_schemes` | INTEGER | | Count of active investment schemes managed |

---

## 8. Table: `fact_sip_industry` (Fact Table)
Contains monthly industry-wide aggregate SIP statistics reported by AMFI.

| Column | Data Type | Key | Description |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | PK | Reference month in YYYY-MM format |
| `sip_inflow_crore` | REAL | | Total industry SIP contributions in Rs. Crores |
| `active_sip_accounts_crore` | REAL | | Count of active SIP accounts in Crores |
| `new_sip_accounts_lakh` | REAL | | Count of newly registered SIPs in Lakhs |
| `sip_aum_lakh_crore` | REAL | | Total assets invested in SIP portfolios in Rs. Lakh Crores |
| `yoy_growth_pct` | REAL | | Year-on-Year growth rate of monthly SIP inflows (%) |
