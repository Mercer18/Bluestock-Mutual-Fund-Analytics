# Bluestock Mutual Fund Analytics – Power BI Dashboard Build Guide

This guide provides step-by-step instructions for building the 4-page Mutual Fund Analytics dashboard in Power BI. It includes data connections, table relationships, DAX formulas, visualization configurations, and interactive features.

---

## 1. Data Loading & Model Setup

### Data Source Loading
1. Open Power BI Desktop.
2. Under the Home tab, click Get Data > Text/CSV.
3. Import the following 10 cleaned CSV files from `Capstone/data/processed/` and the reports files:
   - `01_fund_master_clean.csv` (Rename table to `dim_fund`)
   - `02_nav_history_clean.csv` (Rename table to `fact_nav`)
   - `03_aum_by_fund_house_clean.csv` (Rename table to `fact_aum`)
   - `04_monthly_sip_inflows_clean.csv` (Rename table to `fact_sip_industry`)
   - `05_category_inflows_clean.csv` (Rename table to `fact_category_inflows`)
   - `06_industry_folio_count_clean.csv` (Rename table to `fact_folio_industry`)
   - `10_benchmark_indices_clean.csv` (Rename table to `dim_benchmark_indices`)
   - `08_investor_transactions_clean.csv` (Rename table to `fact_transactions`)
   - `fund_scorecard.csv` (Rename table to `fact_scorecard`)
   - `alpha_beta.csv` (Rename table to `fact_alpha_beta`)
4. Verify that all tables load correctly in the Power Query editor and click Close & Apply.

### Theme Configuration
1. Go to the View tab in the top ribbon.
2. Click the dropdown arrow in the Themes gallery.
3. Select Browse for themes and choose the `bluestock_theme.json` file in the `Capstone/dashboard/` folder. This will load the Bluestock brand colors (Royal Blue `#414BEA` and Orange `#F05537`).

### Establishing Relationships (Model View)
Navigate to the Model View on the left sidebar and establish the following relationships (all default to one-to-many, single direction unless noted):
1. `dim_fund[amfi_code]` to `fact_nav[amfi_code]`
2. `dim_fund[amfi_code]` to `fact_transactions[amfi_code]`
3. `dim_fund[amfi_code]` to `fact_scorecard[amfi_code]` (One-to-one, bi-directional)
4. `dim_fund[amfi_code]` to `fact_alpha_beta[amfi_code]` (One-to-one, bi-directional)
5. Create a Date table if needed, or link the `dim_date` (or date column in tables) to keep dates aligned. For this project, you can relate the date columns across the transaction, NAV, and index tables directly.

---

## 2. DAX Measures & Calculations

Create a new table named `_Measures` to store the following calculations:

### Total Schemes
```dax
Total Schemes = DISTINCTCOUNT(dim_fund[amfi_code])
```

### Total Industry AUM (Latest)
```dax
Total Industry AUM (Cr) = 
CALCULATE(
    SUM(fact_aum[aum_crore]),
    FILTER(
        fact_aum,
        fact_aum[date] = MAX(fact_aum[date])
    )
)
```

### Total SIP Inflow (Latest Monthly)
```dax
Latest SIP Inflow (Cr) = 
CALCULATE(
    SUM(fact_sip_industry[sip_inflow_crore]),
    FILTER(
        fact_sip_industry,
        fact_sip_industry[month] = MAX(fact_sip_industry[month])
    )
)
```

### Total Folios (Latest Monthly)
```dax
Latest Folios (Cr) = 
CALCULATE(
    MAX(fact_sip_industry[active_sip_accounts_crore]),
    FILTER(
        fact_sip_industry,
        fact_sip_industry[month] = MAX(fact_sip_industry[month])
    )
)
```

### Average Transaction Amount
```dax
Average SIP Amount = 
CALCULATE(
    AVERAGE(fact_transactions[amount]),
    fact_transactions[type] = "SIP"
)
```

### Transaction Volume
```dax
Transaction Volume = COUNT(fact_transactions[tx_id])
```

---

## 3. Page-by-Page Layout Guide

### Page 1 — Industry Overview
This page provides a high-level summary of the Indian mutual fund industry's size, schemes, and overall AUM growth.
1. KPI Card 1: Total AUM (Cr) — Set to `Total Industry AUM (Cr)` and format as Currency (₹81L Crore or ₹81 Trillion).
2. KPI Card 2: Latest Monthly SIP Inflows — Set to `Latest SIP Inflow (Cr)` (approx. ₹31K Crore).
3. KPI Card 3: Active Folios — Set to `Latest Folios (Cr)` (approx. 26.12 Crore).
4. KPI Card 4: Total Schemes — Set to `Total Schemes` (1,908 schemes).
5. Line Chart: Industry AUM Trend (2022-2025)
   - X-Axis: `fact_aum[date]` (grouped by Year-Month)
   - Y-Axis: `fact_aum[aum_crore]`
   - Title: "Industry-Wide AUM Growth Trend"
6. Bar Chart: Top AMCs by AUM
   - Axis/Category: `dim_fund[fund_house]`
   - Values: `fact_aum[aum_crore]`
   - Sort: Descending by AUM.

### Page 2 — Fund Performance Analytics
This page evaluates the risk-adjusted returns and scorecards of the 40 mutual fund schemes.
1. Scatter Plot: Risk vs Return Profile
   - X-Axis: `fact_scorecard[cagr_3yr_pct]` (Return)
   - Y-Axis: `fact_alpha_beta[volatility_ann_pct]` (Risk/StdDev)
   - Legend/Details: `dim_fund[scheme_name]`
   - Size/Bubble Size: `fact_scorecard[composite_score]` (or proxy AUM)
   - Title: "Risk-Adjusted Return Profile: 3-Yr CAGR vs Annualized Volatility"
2. Table: Fund Scorecard Table
   - Columns: `fact_scorecard[rank]`, `dim_fund[scheme_name]`, `dim_fund[category]`, `fact_scorecard[cagr_3yr_pct]`, `fact_scorecard[sharpe]`, `fact_alpha_beta[alpha_pct]`, `fact_scorecard[max_dd_pct]`, `fact_scorecard[composite_score]`
   - Enable sorting on any column (specifically the Composite Score).
3. Line Chart: NAV vs Benchmark
   - X-Axis: `fact_nav[date]` (Daily)
   - Y-Axis: `fact_nav[nav]` and `dim_benchmark_indices[close_value]` (Dual axis or normalized line)
4. Slicers (Top Ribbon):
   - Fund House (`dim_fund[fund_house]`)
   - Category (`dim_fund[category]`)
   - Plan (`dim_fund[plan]`)

### Page 3 — Investor Analytics
This page analyzes the demographic and geographic distributions of investors.
1. Bar Chart: Transaction Amount by State
   - Axis: `fact_transactions[state]`
   - Values: Sum of `fact_transactions[amount]`
   - Sort: Descending by total amount.
2. Donut Chart: Transaction Type Split
   - Legend: `fact_transactions[type]` (SIP, Lumpsum, Redemption)
   - Values: Count of transactions or sum of transaction amounts.
3. Column Chart: Age Group vs Average SIP Amount
   - X-Axis: `fact_transactions[age_group]`
   - Y-Axis: `Average SIP Amount`
4. Line Chart: Monthly Transaction Volume
   - X-Axis: `fact_transactions[date]` (grouped by Year-Month)
   - Y-Axis: `Transaction Volume`
5. Slicers:
   - State (`fact_transactions[state]`)
   - Age Group (`fact_transactions[age_group]`)
   - City Tier (`fact_transactions[city_tier]`)

### Page 4 — SIP & Market Trends
This page explores monthly inflows and compares them with broader equity market trends.
1. Dual-Axis Line and Stacked Column Chart: SIP Inflows vs Market
   - X-Axis: `fact_sip_industry[month]`
   - Column Values (Y-Axis 1): `fact_sip_industry[sip_inflow_crore]` (Bar)
   - Line Values (Y-Axis 2): Close value of `NIFTY50` from `dim_benchmark_indices` (Line)
   - Title: "Monthly SIP Inflow vs Nifty 50 Index Trend (2022-2025)"
2. Heatmap / Matrix: Category Inflows Matrix
   - Rows: Category (`fact_category_inflows[category]`)
   - Columns: Year (`fact_category_inflows[date]` or year extraction)
   - Values: Sum of Net Inflow
   - Apply Conditional Formatting > Background Color (gradient from White to Royal Blue).
3. Horizontal Bar Chart: Top 5 Categories by Net Inflow (FY25)
   - Y-Axis: Category (`fact_category_inflows[category]`)
   - X-Axis: Sum of Net Inflow
   - Filter: Top 5 by value for Year 2025/FY25.

---

## 4. Adding Interactivity & Polishing

### Drill-Through Configuration
To enable drill-through from the Fund scorecard table on Page 2 to a detailed NAV history detail page:
1. Create a new page named NAV Detail Page.
2. Add a Line Chart displaying `fact_nav[date]` (X-Axis) and `fact_nav[nav]` (Y-Axis).
3. In the NAV Detail Page's visual properties, locate the Drill-through section in the Fields pane.
4. Drag and drop `dim_fund[scheme_name]` into the Drill-through filters field.
5. In Page 2, users can now right-click a fund scheme in the Scorecard table and select Drill-through > NAV Detail Page.

### Tooltips Setup
1. Hover over any chart.
2. Go to the Format visual tab.
3. Ensure Tooltips is toggled On.
4. Add relevant columns like Fund Category, Sharpe Ratio, or Total Transactions to the Tooltips field to provide rich context on hover.

### Theme & Logo
1. Insert the Bluestock logo in the top-left corner of each page (Insert > Image).
2. Use the Header banner colored in Royal Blue (`#414BEA`) with White text for page titles to ensure a highly premium, unified look.
