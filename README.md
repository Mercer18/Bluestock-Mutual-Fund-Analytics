# Bluestock Mutual Fund Analytics Platform

An end-to-end data engineering, ETL, database storage, quantitative risk modeling, and business intelligence platform to ingest, process, clean, analyze, and visualize Indian mutual fund data (spanning 40 schemes over 4.4 years).

---

## Project Objectives

1. **Robust Ingestion (Day 1):** Python-based ETL client fetching live Net Asset Value (NAV) details from the Association of Mutual Funds in India (AMFI) open API with retry-backoff mechanisms.
2. **Relational Modeling (Day 2):** SQLite Star Schema database load utilizing SQLAlchemy with primary/foreign constraints and index optimizations.
3. **Exploratory Analysis (Day 3):** Python-based data science visualizations (16 plots) capturing demographics, city tiers, and sector allocations.
4. **Performance Scorecard (Day 4):** Quantitative evaluation of returns (CAGR) and volatility-adjusted benchmarks (Sharpe, Sortino, Alpha, Beta, Max Drawdowns).
5. **Dashboard Development (Day 5):** Interactive 4-page Power BI dashboard designed with Bluestock's custom brand colors and visual guides.
6. **Advanced Risk Modeling (Day 6):** Percentile-based tail-loss calculations (95% VaR, CVaR), stock diversification metrics (HHI), and systematic transaction cohort retention tables.
7. **Pipeline Coordination & Reporting (Day 7):** Automated master pipeline script, professional 20-page PDF report, 12-slide presentation deck, and Git deployment.

---

## Directory Structure

```text
Capstone/
├── Final_Report.pdf              # Day 7: Automated 20-Page Final Report PDF (reportlab)
├── Bluestock_MF_Presentation.pptx # Day 7: Automated 12-Slide Presentation PPTX (python-pptx)
├── run_pipeline.py               # Day 7: Master execution pipeline script
├── recommender.py                # Day 6: CLI Interactive Fund Recommender Script (Root Copy)
├── fund_scorecard.csv            # Day 4: Top ranked schemes composite scorecard (Root Copy)
├── alpha_beta.csv                # Day 4: Risk and return metrics (Root Copy)
├── var_cvar_report.csv           # Day 6: Mutual Fund Historical VaR and CVaR Report (Root Copy)
├── rolling_sharpe_chart.png      # Day 6: Rolling 90-day Sharpe Ratio Chart (Root Copy)
├── benchmark_comparison_chart.png # Day 4: 3-Year cumulative performance vs Niftys (Root Copy)
├── requirements.txt              # Project package dependencies
├── README.md                     # Comprehensive project documentation
├── dashboard/
│   ├── bluestock_theme.json      # Day 5: Custom Power BI color theme JSON
│   └── dashboard_guide.md        # Day 5: Detailed dashboard build guide
├── data/
│   ├── raw/                      # Ingested raw datasets (including live NAVs from API)
│   ├── processed/                # Transformed & cleaned dimension and fact CSV datasets
│   └── db/                       # Relational SQLite database (bluestock_mf.db)
├── notebooks/
│   ├── 01_data_ingestion.ipynb   # Day 1: Loads and inspects CSV metadata & validates AMFI codes
│   ├── 02_database_load.ipynb    # Day 2: Loads cleaned CSVs to SQLite & executes 10 test SQL queries
│   ├── 03_eda_analysis.ipynb     # Day 3: Exploratory Data Analysis (16 plots)
│   ├── Performance_Analytics.ipynb # Day 4: Quantitative scorecard notebook
│   └── Advanced_Analytics.ipynb  # Day 6: Advanced analytics and insights copy
├── scripts/
│   ├── live_nav_fetch.py         # Day 1: Ingests live NAVs from AMFI REST API
│   ├── generate_analytics.py     # Day 4: Computes quantitative performance metrics
│   ├── generate_day6_analytics.py # Day 6: Computes VaR, Sharpe, Cohorts, and HHI
│   ├── recommender.py            # Day 6: Interactive recommender script
│   ├── generate_final_report.py  # Day 7: Programmatic PDF report builder
│   ├── generate_presentation.py  # Day 7: Programmatic PPTX presentation builder
│   └── verify_analytics.py       # Day 4: Verification script
├── sql/
│   ├── schema.sql                # Day 2: SQLite Star Schema DDL definition
│   └── queries.sql               # Day 2: 10 analytical verification SQL queries
└── reports/
    ├── Final_Report.pdf          # Final Report PDF Copy
    ├── Bluestock_MF_Presentation.pptx # Presentation PPTX Copy
    ├── data_dictionary.md        # Day 2: Database schema reference documentation
    ├── var_cvar_report.csv       # Day 6: VaR and CVaR Report CSV Copy
    ├── sector_hhi_report.csv     # Day 6: Sector HHI Index Report CSV
    ├── cohort_analysis_report.csv # Day 6: Cohort Analysis Report CSV
    ├── sip_continuity_report.csv # Day 6: SIP Continuity Report CSV
    └── figures/
        ├── rolling_sharpe_chart.png # Day 6: Rolling Sharpe Chart Copy
        └── [01-16]_*.png            # Day 3: The 16 EDA plot figures
```

---

## Setup & Execution Guide

### 1. Environment Initialization
Create and activate your Python virtual environment, then install all project requirements:
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install package dependencies
pip install -r requirements.txt
```

### 2. Running the Master Execution Pipeline
To run the entire end-to-end pipeline (fetching live API data, loading the database, calculating performance, computing risk factors, and auto-compiling the PDF report and PowerPoint presentation) with a single command:
```bash
python run_pipeline.py
```
This coordinates the execution of all ingestion, analysis, and generation stages in sequence.

### 3. Testing the Interactive Fund Recommender
Launch the command-line recommender system to get mutual fund suggestions matching your risk profile:
```bash
python recommender.py
```
Enter risk appetite (`Low`, `Moderate`, or `High`) to output a ranked table of the top 3 schemes selected by Sharpe ratio.

---

## Relational Database Star Schema

The database is structured as a **Star Schema** optimized for high-performance BI reporting. Table schemas include:
* **dim_fund** (amfi_code [PK], scheme_name, expense_ratio_pct, category, benchmark)
* **dim_date** (date [PK], year, month, quarter, is_weekday)
* **fact_nav** (nav_id [PK], amfi_code [FK], date [FK], nav)
* **fact_transactions** (transaction_id [PK], investor_id, amfi_code [FK], date [FK], type, amount)
* **fact_portfolio** (portfolio_id [PK], amfi_code [FK], stock_symbol, weight_pct, sector, date [FK])
* **fact_aum** (aum_id [PK], fund_house, date [FK], aum_crore, num_schemes)
* **fact_sip_industry** (sip_id [PK], month, total_sip_accounts, total_sip_inflow_inr, yoy_growth_pct)

---

## Key Analytics & Ratios Calculated

* **CAGR:** Compounded Annual Growth Rate over 1, 3, and 5-year periods.
* **Annualized Volatility:** Standard deviation of daily returns annualized over a 252-day basis.
* **Sharpe & Sortino Ratios:** Risk-adjusted return indices benchmarked against a 6.5% risk-free rate.
* **Alpha & Beta:** OLS regression parameters measuring abnormal return and systematic sensitivity vs. the Nifty 100 benchmark.
* **Maximum Drawdowns:** Worst peak-to-trough drops and recovery periods.
* **Value at Risk (95% VaR & CVaR):** Daily tail-loss potential modeling.
* **Herfindahl-Hirschman Index (HHI):** Portfolio sector concentrations.
* **Cohort Analysis:** Retention sizing grouped by investor signup year.

---

## BI Dashboard Layout

The 4-page Power BI dashboard incorporates the custom `bluestock_theme.json` styling with rounded visual cards, subtle drop shadows, and brand colors (#414BEA and #F05537).
1. **Industry Overview:** KPI cards, Treemap of category AUM, and monthly SIP trends.
2. **Fund Performance:** CAGR vs. Volatility scatter plots, scorecard rank tables, and NAV vs. benchmark trendlines.
3. **Investor Analytics:** Geographic transaction state heatmaps, age brackets vs. average SIP, and payment donuts.
4. **SIP & Market Trends:** Dual-axis charts comparing monthly inflows vs. the Nifty 50 Index.

Detailed formulas and relationships are documented in the [Dashboard Build Guide](file:///x:/CODING/PROJECTS/InternshipWork/Bluestock/Capstone/dashboard/dashboard_guide.md).
