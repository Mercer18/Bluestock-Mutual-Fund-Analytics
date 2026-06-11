"""
generate_analytics.py
Day 4 Capstone Project - Quantitative Performance Scorecard Analytics

This script connects to the SQLite database, computes daily returns, CAGR (1, 3, and 5-year periods),
volatility, Sharpe and Sortino ratios, and regression statistics (Alpha and Beta vs Nifty benchmarks).
It aggregates these metrics to construct a ranked composite scorecard, outputs the result CSVs,
and generates the 3-Year performance chart vs benchmarks.
"""

import os
import sqlite3
import json
import pandas as pd
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for professional charts
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'axes.edgecolor': '#cccccc',
    'axes.linewidth': 0.8,
    'grid.color': '#eeeeee',
    'grid.linestyle': '-',
    'figure.titlesize': 14,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9
})

def run_performance_analytics():
    base_dir = r'x:\CODING\PROJECTS\InternshipWork\Bluestock\Capstone'
    db_path = os.path.join(base_dir, 'data', 'db', 'bluestock_mf.db')
    bench_path = os.path.join(base_dir, 'data', 'processed', '10_benchmark_indices_clean.csv')
    
    print("Connecting to database...")
    conn = sqlite3.connect(db_path)
    
    # 1. Load data
    print("Loading data...")
    df_funds = pd.read_sql_query("SELECT amfi_code, scheme_name, expense_ratio_pct, benchmark, category FROM dim_fund", conn)
    df_nav = pd.read_sql_query("SELECT amfi_code, date, nav FROM fact_nav ORDER BY amfi_code, date", conn)
    df_nav['date'] = pd.to_datetime(df_nav['date'])
    
    df_bench = pd.read_csv(bench_path)
    df_bench['date'] = pd.to_datetime(df_bench['date'])
    
    print(f"Loaded {len(df_funds)} funds, {len(df_nav)} NAV rows, and {len(df_bench)} benchmark rows.")
    
    # 2. Daily Returns
    print("Computing daily returns...")
    df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change().fillna(0.0)
    
    # 3. CAGR calculations
    # End date: 2026-05-29 (max available in dataset)
    # 1yr start: 2025-05-29
    # 3yr start: 2023-05-29
    # 5yr start (inception): 2022-01-03
    end_date = pd.to_datetime('2026-05-29')
    start_1yr = pd.to_datetime('2025-05-29')
    start_3yr = pd.to_datetime('2023-05-29')
    start_5yr = pd.to_datetime('2022-01-03')
    
    n_days_5yr = (end_date - start_5yr).days
    n_years_5yr = n_days_5yr / 365.25 # 4.40246 years
    
    cagr_results = []
    
    # Benchmark daily returns
    df_bench['daily_return'] = df_bench.groupby('index_name')['close_value'].pct_change().fillna(0.0)
    
    # Pivot benchmark close values for ease of regression and plotting
    df_bench_pivot = df_bench.pivot(index='date', columns='index_name', values='close_value')
    df_bench_ret_pivot = df_bench.pivot(index='date', columns='index_name', values='daily_return')
    
    # Benchmark mapping dictionary
    benchmark_mapping = {
        'NIFTY 100 TRI': 'NIFTY100',
        'BSE 250 SmallCap TRI': 'BSE_SMALLCAP',
        'CRISIL Dynamic Gilt Index': 'CRISIL_GILT',
        'NIFTY Midcap 150 TRI': 'NIFTY_MIDCAP150',
        'CRISIL Short Term Bond Index': 'CRISIL_LIQUID',
        'NIFTY 500 TRI': 'NIFTY500',
        'CRISIL Liquid Fund AI Index': 'CRISIL_LIQUID',
        'NIFTY 50 TRI': 'NIFTY50',
        'NIFTY Midcap 50 TRI': 'NIFTY_MIDCAP150',
        'NIFTY Large Midcap 250 TRI': 'NIFTY500'
    }
    
    fund_metrics = []
    
    for idx, fund_row in df_funds.iterrows():
        code = fund_row['amfi_code']
        name = fund_row['scheme_name']
        exp_ratio = fund_row['expense_ratio_pct']
        bench_desc = fund_row['benchmark']
        category = fund_row['category']
        
        # Get fund NAV history
        fund_nav = df_nav[df_nav['amfi_code'] == code].sort_values('date').copy()
        
        # Check that we have the full date range
        nav_end = fund_nav[fund_nav['date'] == end_date]['nav'].values[0]
        nav_1yr = fund_nav[fund_nav['date'] == start_1yr]['nav'].values[0]
        nav_3yr = fund_nav[fund_nav['date'] == start_3yr]['nav'].values[0]
        nav_5yr = fund_nav[fund_nav['date'] == start_5yr]['nav'].values[0]
        
        # Compute CAGR
        cagr_1yr = (nav_end / nav_1yr) ** (1 / 1.0) - 1
        cagr_3yr = (nav_end / nav_3yr) ** (1 / 3.0) - 1
        cagr_5yr = (nav_end / nav_5yr) ** (1 / n_years_5yr) - 1
        
        # Clean daily returns (drop first row since it's NaN return)
        daily_ret = fund_nav['daily_return'].values[1:]
        
        # Sharpe Ratio (Rf = 6.5% annual -> 6.5%/252 daily)
        mean_ret_ann = np.mean(daily_ret) * 252
        vol_ann = np.std(daily_ret, ddof=1) * np.sqrt(252)
        sharpe = (mean_ret_ann - 0.065) / vol_ann if vol_ann > 0 else 0.0
        
        # Sortino Ratio
        downside_ret = daily_ret[daily_ret < 0]
        downside_vol_ann = np.std(downside_ret, ddof=1) * np.sqrt(252) if len(downside_ret) > 1 else 0.0
        sortino = (mean_ret_ann - 0.065) / downside_vol_ann if downside_vol_ann > 0 else 0.0
        
        # Alpha and Beta against Nifty 100
        nifty100_ret = df_bench_ret_pivot['NIFTY100'].loc[fund_nav['date']].values[1:]
        
        slope, intercept, r_val, p_val, std_err = scipy.stats.linregress(nifty100_ret, daily_ret)
        beta = slope
        alpha = intercept * 252 # Annualized alpha
        
        # Maximum Drawdown
        fund_nav['running_max'] = fund_nav['nav'].cummax()
        fund_nav['drawdown'] = fund_nav['nav'] / fund_nav['running_max'] - 1
        max_dd = fund_nav['drawdown'].min()
        
        # Find worst drawdown date range
        trough_idx = fund_nav['drawdown'].idxmin()
        trough_row = fund_nav.loc[trough_idx]
        trough_date = trough_row['date']
        
        # Preceding peak date
        preceding_navs = fund_nav[fund_nav['date'] <= trough_date]
        peak_idx = preceding_navs['nav'].idxmax()
        peak_date = fund_nav.loc[peak_idx]['date']
        
        # Find recovery date (first date after trough where nav >= peak nav)
        peak_nav = fund_nav.loc[peak_idx]['nav']
        post_trough = fund_nav[fund_nav['date'] > trough_date]
        recovery_rows = post_trough[post_trough['nav'] >= peak_nav]
        if len(recovery_rows) > 0:
            recovery_date = recovery_rows.iloc[0]['date'].strftime('%Y-%m-%d')
        else:
            recovery_date = "Not Recovered"
            
        # Tracking Error against its respective benchmark
        bench_col = benchmark_mapping.get(bench_desc, 'NIFTY100')
        bench_ret = df_bench_ret_pivot[bench_col].loc[fund_nav['date']].values[1:]
        
        tracking_err = np.std(daily_ret - bench_ret, ddof=1) * np.sqrt(252)
        
        fund_metrics.append({
            'amfi_code': code,
            'scheme_name': name,
            'category': category,
            'expense_ratio_pct': exp_ratio,
            'benchmark': bench_desc,
            'benchmark_col': bench_col,
            'cagr_1yr': cagr_1yr,
            'cagr_3yr': cagr_3yr,
            'cagr_5yr': cagr_5yr,
            'mean_daily_return': np.mean(daily_ret),
            'volatility_ann': vol_ann,
            'sharpe': sharpe,
            'sortino': sortino,
            'alpha': alpha,
            'beta': beta,
            'max_dd': max_dd,
            'peak_date': peak_date.strftime('%Y-%m-%d'),
            'trough_date': trough_date.strftime('%Y-%m-%d'),
            'recovery_date': recovery_date,
            'tracking_error': tracking_err
        })
        
    df_metrics = pd.DataFrame(fund_metrics)
    
    # 4. Construct Scorecard
    print("Constructing scorecard ranks...")
    # Percentile ranks: scaled 0 to 100
    df_metrics['rank_3yr'] = df_metrics['cagr_3yr'].rank(pct=True) * 100
    df_metrics['rank_sharpe'] = df_metrics['sharpe'].rank(pct=True) * 100
    df_metrics['rank_alpha'] = df_metrics['alpha'].rank(pct=True) * 100
    df_metrics['rank_expense'] = df_metrics['expense_ratio_pct'].rank(ascending=False, pct=True) * 100 # Lower is better
    df_metrics['rank_max_dd'] = df_metrics['max_dd'].rank(ascending=True, pct=True) * 100 # Max DD is negative, so less negative (larger value) is better. ascending=True is correct.
    
    # Composite Score
    df_metrics['composite_score'] = (
        0.30 * df_metrics['rank_3yr'] +
        0.25 * df_metrics['rank_sharpe'] +
        0.20 * df_metrics['rank_alpha'] +
        0.15 * df_metrics['rank_expense'] +
        0.10 * df_metrics['rank_max_dd']
    )
    
    # Sort by composite score
    df_metrics = df_metrics.sort_values('composite_score', ascending=False).reset_index(drop=True)
    df_metrics['rank'] = df_metrics.index + 1
    
    # Save Alpha/Beta results
    print("Saving alpha_beta.csv...")
    df_alpha_beta = df_metrics[['amfi_code', 'scheme_name', 'alpha', 'beta', 'volatility_ann']].copy()
    # Format percentages for readability
    df_alpha_beta['alpha'] = df_alpha_beta['alpha'] * 100
    df_alpha_beta['volatility_ann'] = df_alpha_beta['volatility_ann'] * 100
    
    # Rename columns for clarity
    df_alpha_beta = df_alpha_beta.rename(columns={
        'alpha': 'alpha_pct',
        'volatility_ann': 'volatility_ann_pct'
    })
    
    alpha_beta_csv_path = os.path.join(base_dir, 'alpha_beta.csv')
    df_alpha_beta.to_csv(alpha_beta_csv_path, index=False)
    
    # Save Fund Scorecard results
    print("Saving fund_scorecard.csv...")
    df_scorecard = df_metrics[[
        'rank', 'amfi_code', 'scheme_name', 'category', 'expense_ratio_pct', 
        'cagr_3yr', 'sharpe', 'alpha', 'max_dd', 'composite_score'
    ]].copy()
    
    # Format values as percentages/ratios for clarity
    df_scorecard['cagr_3yr'] = df_scorecard['cagr_3yr'] * 100
    df_scorecard['alpha'] = df_scorecard['alpha'] * 100
    df_scorecard['max_dd'] = df_scorecard['max_dd'] * 100
    
    df_scorecard = df_scorecard.rename(columns={
        'cagr_3yr': 'cagr_3yr_pct',
        'alpha': 'alpha_pct',
        'max_dd': 'max_dd_pct'
    })
    
    scorecard_csv_path = os.path.join(base_dir, 'fund_scorecard.csv')
    df_scorecard.to_csv(scorecard_csv_path, index=False)
    
    # Copy to reports/ directory as well
    os.makedirs(os.path.join(base_dir, 'reports'), exist_ok=True)
    df_alpha_beta.to_csv(os.path.join(base_dir, 'reports', 'alpha_beta.csv'), index=False)
    df_scorecard.to_csv(os.path.join(base_dir, 'reports', 'fund_scorecard.csv'), index=False)
    
    # 5. Benchmark Comparison Chart (3-Year cumulative performance of top 5 vs Nifty 50 and Nifty 100)
    print("Generating benchmark comparison chart...")
    top_5_funds = df_metrics.head(5)
    
    plt.figure(figsize=(12, 7))
    
    # Period: 2023-05-29 to 2026-05-29
    dates_3yr = pd.date_range(start='2023-05-29', end='2026-05-29', freq='D')
    
    # Plot Benchmarks first
    nifty50_prices = df_bench_pivot['NIFTY50'].loc[dates_3yr]
    nifty50_cum = (nifty50_prices / nifty50_prices.iloc[0]) * 100
    plt.plot(nifty50_cum.index, nifty50_cum.values, label='Nifty 50 TRI (Benchmark)', color='#555555', linewidth=2.0, linestyle='--')
    
    nifty100_prices = df_bench_pivot['NIFTY100'].loc[dates_3yr]
    nifty100_cum = (nifty100_prices / nifty100_prices.iloc[0]) * 100
    plt.plot(nifty100_cum.index, nifty100_cum.values, label='Nifty 100 TRI (Benchmark)', color='#888888', linewidth=2.0, linestyle='-.')
    
    # Palette for Top 5 funds
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for idx, fund_row in top_5_funds.iterrows():
        code = fund_row['amfi_code']
        name = fund_row['scheme_name']
        short_name = name.split(" - ")[0] # Clean for legend
        
        fund_nav = df_nav[(df_nav['amfi_code'] == code) & (df_nav['date'].isin(dates_3yr))].sort_values('date')
        
        # Normalize to start at 100
        nav_start = fund_nav['nav'].iloc[0]
        fund_cum = (fund_nav['nav'] / nav_start) * 100
        
        plt.plot(fund_nav['date'], fund_cum, label=f"{short_name} (Rank {fund_row['rank']})", color=colors[idx], linewidth=1.8)
        
    plt.title("3-Year Cumulative Performance Comparison: Top 5 Funds vs Benchmarks (2023-2026)", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Date", fontsize=11, labelpad=10)
    plt.ylabel("Normalized Value (Base = 100 on 2023-05-29)", fontsize=11, labelpad=10)
    plt.legend(loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#dddddd')
    plt.tight_layout()
    
    # Save chart PNG
    chart_png_path = os.path.join(base_dir, 'reports', 'benchmark_comparison_chart.png')
    plt.savefig(chart_png_path, dpi=300)
    plt.savefig(os.path.join(base_dir, 'benchmark_comparison_chart.png'), dpi=300)
    plt.close()
    
    print(f"Benchmark comparison chart saved to {chart_png_path}")
    
    # 6. Generate Performance_Analytics.ipynb
    print("Generating Jupyter notebook notebooks/Performance_Analytics.ipynb...")
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Capstone Project I: Mutual Fund Analytics\n",
                    "## Day 4: Fund Performance Analytics & Scorecard Calculation\n",
                    "\n",
                    "This notebook implements the quantitative analysis of 40 mutual fund schemes over a 4.4-year period (from `2022-01-03` to `2026-05-29`).\n",
                    "\n",
                    "### Tasks Performed:\n",
                    "1. **Compute Daily Returns** and validate distribution.\n",
                    "2. **Compute CAGR** for 1-Year, 3-Year, and 5-Year (Max History).\n",
                    "3. **Compute Sharpe and Sortino Ratios** ($R_f = 6.5\\%$) to rank all 40 funds.\n",
                    "4. **Compute Alpha and Beta** via OLS regression against the Nifty 100 benchmark.\n",
                    "5. **Compute Maximum Drawdown** and identify peak-to-trough worst date ranges.\n",
                    "6. **Build a Composite Fund Scorecard (0-100)** to rank funds using a weighted rank-based system.\n",
                    "7. **Plot Benchmark Comparison Chart** for the top 5 funds vs Nifty 50 and Nifty 100 over a 3-year period and calculate tracking errors."
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 1. Setup & Data Loading"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import os\n",
                    "import sqlite3\n",
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import scipy.stats\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "\n",
                    "# Paths\n",
                    "base_dir = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))\n",
                    "db_path = os.path.join(base_dir, 'data', 'db', 'bluestock_mf.db')\n",
                    "bench_path = os.path.join(base_dir, 'data', 'processed', '10_benchmark_indices_clean.csv')\n",
                    "\n",
                    "conn = sqlite3.connect(db_path)\n",
                    "\n",
                    "# Load Fund Info and NAV History\n",
                    "df_funds = pd.read_sql_query(\"SELECT amfi_code, scheme_name, expense_ratio_pct, benchmark, category FROM dim_fund\", conn)\n",
                    "df_nav = pd.read_sql_query(\"SELECT amfi_code, date, nav FROM fact_nav ORDER BY amfi_code, date\", conn)\n",
                    "df_nav['date'] = pd.to_datetime(df_nav['date'])\n",
                    "\n",
                    "df_bench = pd.read_csv(bench_path)\n",
                    "df_bench['date'] = pd.to_datetime(df_bench['date'])\n",
                    "\n",
                    "print(f\"Loaded {len(df_funds)} funds, {len(df_nav)} NAV rows, and {len(df_bench)} benchmark rows.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 2. Compute Daily Returns & Validate Distribution"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Compute daily return for all funds\n",
                    "df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change().fillna(0.0)\n",
                    "\n",
                    "# Summary statistics of returns across all funds\n",
                    "returns_summary = df_nav.groupby('amfi_code')['daily_return'].describe()\n",
                    "print(\"Daily Returns Summary Statistics (First 5 Funds):\")\n",
                    "display(returns_summary.head())\n",
                    "\n",
                    "# Plot Return Distributions (Combined Histogram)\n",
                    "plt.figure(figsize=(10, 6))\n",
                    "sns.histplot(df_nav['daily_return'], bins=100, kde=True, color='#1f77b4')\n",
                    "plt.title(\"Distribution of Daily Returns Across All 40 Funds (2022-2026)\", fontsize=12, fontweight='bold')\n",
                    "plt.xlabel(\"Daily Return\")\n",
                    "plt.ylabel(\"Frequency\")\n",
                    "plt.tight_layout()\n",
                    "plt.show()"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 3. Compute CAGR (1-Year, 3-Year, 5-Year Proxy)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Setup periods\n",
                    "end_date = pd.to_datetime('2026-05-29')\n",
                    "start_1yr = pd.to_datetime('2025-05-29')\n",
                    "start_3yr = pd.to_datetime('2023-05-29')\n",
                    "start_5yr = pd.to_datetime('2022-01-03') # Max available history\n",
                    "\n",
                    "n_years_5yr = (end_date - start_5yr).days / 365.25\n",
                    "print(f\"Max available history period: {n_years_5yr:.4f} years.\")\n",
                    "\n",
                    "cagr_list = []\n",
                    "\n",
                    "for code, group in df_nav.groupby('amfi_code'):\n",
                    "    group = group.sort_values('date')\n",
                    "    \n",
                    "    nav_end = group[group['date'] == end_date]['nav'].values[0]\n",
                    "    nav_1yr = group[group['date'] == start_1yr]['nav'].values[0]\n",
                    "    nav_3yr = group[group['date'] == start_3yr]['nav'].values[0]\n",
                    "    nav_5yr = group[group['date'] == start_5yr]['nav'].values[0]\n",
                    "    \n",
                    "    cagr_1 = (nav_end / nav_1yr) ** (1 / 1.0) - 1\n",
                    "    cagr_3 = (nav_end / nav_3yr) ** (1 / 3.0) - 1\n",
                    "    cagr_5 = (nav_end / nav_5yr) ** (1 / n_years_5yr) - 1\n",
                    "    \n",
                    "    cagr_list.append({\n",
                    "        'amfi_code': code,\n",
                    "        'cagr_1yr_pct': cagr_1 * 100,\n",
                    "        'cagr_3yr_pct': cagr_3 * 100,\n",
                    "        'cagr_5yr_pct': cagr_5 * 100\n",
                    "    })\n",
                    "\n",
                    "df_cagr = pd.DataFrame(cagr_list)\n",
                    "df_cagr_comp = pd.merge(df_funds[['amfi_code', 'scheme_name']], df_cagr, on='amfi_code')\n",
                    "\n",
                    "print(\"CAGR Comparison Table (First 10 Funds):\")\n",
                    "display(df_cagr_comp.head(10))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 4. Compute Sharpe & Sortino Ratios"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "ratios_list = []\n",
                    "Rf_daily = 0.065 / 252 # Annual risk-free rate of 6.5%\n",
                    "\n",
                    "for code, group in df_nav.groupby('amfi_code'):\n",
                    "    daily_ret = group.sort_values('date')['daily_return'].values[1:] # Drop first day return (NaN -> 0)\n",
                    "    \n",
                    "    mean_daily = np.mean(daily_ret)\n",
                    "    std_daily = np.std(daily_ret, ddof=1)\n",
                    "    \n",
                    "    # Sharpe Ratio\n",
                    "    mean_ret_ann = mean_daily * 252\n",
                    "    vol_ann = std_daily * np.sqrt(252)\n",
                    "    sharpe = (mean_ret_ann - 0.065) / vol_ann if vol_ann > 0 else 0.0\n",
                    "    \n",
                    "    # Sortino Ratio (negative returns standard deviation)\n",
                    "    downside_ret = daily_ret[daily_ret < 0]\n",
                    "    downside_std_daily = np.std(downside_ret, ddof=1) if len(downside_ret) > 1 else 0.0\n",
                    "    downside_vol_ann = downside_std_daily * np.sqrt(252)\n",
                    "    sortino = (mean_ret_ann - 0.065) / downside_vol_ann if downside_vol_ann > 0 else 0.0\n",
                    "    \n",
                    "    ratios_list.append({\n",
                    "        'amfi_code': code,\n",
                    "        'volatility_ann_pct': vol_ann * 100,\n",
                    "        'sharpe': sharpe,\n",
                    "        'sortino': sortino\n",
                    "    })\n",
                    "    \n",
                    "df_ratios = pd.DataFrame(ratios_list)\n",
                    "df_ratios_comp = pd.merge(df_funds[['amfi_code', 'scheme_name']], df_ratios, on='amfi_code')\n",
                    "\n",
                    "print(\"Sharpe & Sortino Ratios (Top 10 sorted by Sharpe):\")\n",
                    "display(df_ratios_comp.sort_values('sharpe', ascending=False).head(10))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 5. Compute Alpha & Beta (OLS Regression on Nifty 100)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Calculate Nifty 100 daily returns\n",
                    "df_bench['daily_return'] = df_bench.groupby('index_name')['close_value'].pct_change().fillna(0.0)\n",
                    "df_bench_ret_pivot = df_bench.pivot(index='date', columns='index_name', values='daily_return')\n",
                    "\n",
                    "regression_list = []\n",
                    "\n",
                    "for code, group in df_nav.groupby('amfi_code'):\n",
                    "    fund_ret = group.sort_values('date')['daily_return'].values[1:]\n",
                    "    fund_dates = group.sort_values('date')['date'].values[1:]\n",
                    "    \n",
                    "    # Get Nifty 100 returns aligned to fund dates\n",
                    "    nifty_ret = df_bench_ret_pivot['NIFTY100'].loc[fund_dates].values\n",
                    "    \n",
                    "    # Run OLS Regression\n",
                    "    slope, intercept, r_val, p_val, std_err = scipy.stats.linregress(nifty_ret, fund_ret)\n",
                    "    beta = slope\n",
                    "    alpha = intercept * 252 # Annualized alpha\n",
                    "    \n",
                    "    regression_list.append({\n",
                    "        'amfi_code': code,\n",
                    "        'alpha_pct': alpha * 100,\n",
                    "        'beta': beta\n",
                    "    })\n",
                    "    \n",
                    "df_regression = pd.DataFrame(regression_list)\n",
                    "df_reg_comp = pd.merge(df_funds[['amfi_code', 'scheme_name']], df_regression, on='amfi_code')\n",
                    "\n",
                    "print(\"Alpha and Beta Metrics (Top 10 sorted by Alpha):\")\n",
                    "display(df_reg_comp.sort_values('alpha_pct', ascending=False).head(10))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 6. Compute Maximum Drawdown & Date Range"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "drawdown_list = []\n",
                    "\n",
                    "for code, group in df_nav.groupby('amfi_code'):\n",
                    "    group = group.sort_values('date').copy()\n",
                    "    group['running_max'] = group['nav'].cummax()\n",
                    "    group['drawdown'] = group['nav'] / group['running_max'] - 1\n",
                    "    \n",
                    "    max_dd = group['drawdown'].min()\n",
                    "    trough_idx = group['drawdown'].idxmin()\n",
                    "    trough_row = group.loc[trough_idx]\n",
                    "    trough_date = trough_row['date']\n",
                    "    \n",
                    "    # Preceding Peak Date\n",
                    "    preceding = group[group['date'] <= trough_date]\n",
                    "    peak_idx = preceding['nav'].idxmax()\n",
                    "    peak_row = group.loc[peak_idx]\n",
                    "    peak_date = peak_row['date']\n",
                    "    peak_nav = peak_row['nav']\n",
                    "    \n",
                    "    # Recovery Date\n",
                    "    post_trough = group[group['date'] > trough_date]\n",
                    "    recovery = post_trough[post_trough['nav'] >= peak_nav]\n",
                    "    if len(recovery) > 0:\n",
                    "        rec_date = recovery.iloc[0]['date'].strftime('%Y-%m-%d')\n",
                    "    else:\n",
                    "        rec_date = \"Not Recovered\"\n",
                    "        \n",
                    "    drawdown_list.append({\n",
                    "        'amfi_code': code,\n",
                    "        'max_dd_pct': max_dd * 100,\n",
                    "        'peak_date': peak_date.strftime('%Y-%m-%d'),\n",
                    "        'trough_date': trough_date.strftime('%Y-%m-%d'),\n",
                    "        'recovery_date': rec_date\n",
                    "    })\n",
                    "    \n",
                    "df_drawdown = pd.DataFrame(drawdown_list)\n",
                    "df_dd_comp = pd.merge(df_funds[['amfi_code', 'scheme_name']], df_drawdown, on='amfi_code')\n",
                    "\n",
                    "print(\"Maximum Drawdown Summary (Top 10 sorted by worst drawdown, i.e., lowest DD):\")\n",
                    "display(df_dd_comp.sort_values('max_dd_pct', ascending=True).head(10))"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 7. Construct Composite Fund Scorecard"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Combine all computed metrics\n",
                    "df_metrics = df_funds[['amfi_code', 'scheme_name', 'category', 'expense_ratio_pct', 'benchmark']].copy()\n",
                    "df_metrics = df_metrics.merge(df_cagr, on='amfi_code')\n",
                    "df_metrics = df_metrics.merge(df_ratios, on='amfi_code')\n",
                    "df_metrics = df_metrics.merge(df_regression, on='amfi_code')\n",
                    "df_metrics = df_metrics.merge(df_drawdown, on='amfi_code')\n",
                    "\n",
                    "# Compute Ranks (scaled 0 to 100)\n",
                    "df_metrics['rank_3yr'] = df_metrics['cagr_3yr_pct'].rank(pct=True) * 100\n",
                    "df_metrics['rank_sharpe'] = df_metrics['sharpe'].rank(pct=True) * 100\n",
                    "df_metrics['rank_alpha'] = df_metrics['alpha_pct'].rank(pct=True) * 100\n",
                    "df_metrics['rank_expense'] = df_metrics['expense_ratio_pct'].rank(ascending=False, pct=True) * 100 # Lower is better\n",
                    "df_metrics['rank_max_dd'] = df_metrics['max_dd_pct'].rank(ascending=True, pct=True) * 100 # Less negative is better (ascending=True is correct)\n",
                    "\n",
                    "# Compute Composite Score\n",
                    "df_metrics['composite_score'] = (\n",
                    "    0.30 * df_metrics['rank_3yr'] +\n",
                    "    0.25 * df_metrics['rank_sharpe'] +\n",
                    "    0.20 * df_metrics['rank_alpha'] +\n",
                    "    0.15 * df_metrics['rank_expense'] +\n",
                    "    0.10 * df_metrics['rank_max_dd']\n",
                    ")\n",
                    "\n",
                    "# Sort by score\n",
                    "df_metrics = df_metrics.sort_values('composite_score', ascending=False).reset_index(drop=True)\n",
                    "df_metrics['rank'] = df_metrics.index + 1\n",
                    "\n",
                    "print(\"Top 10 Funds by Composite Performance Scorecard:\")\n",
                    "display(df_metrics[['rank', 'amfi_code', 'scheme_name', 'category', 'cagr_3yr_pct', 'sharpe', 'alpha_pct', 'max_dd_pct', 'composite_score']].head(10))\n",
                    "# Save outputs\n",
                    "df_scorecard = df_metrics[[\n",
                    "    'rank', 'amfi_code', 'scheme_name', 'category', 'expense_ratio_pct',\n",
                    "    'cagr_3yr_pct', 'sharpe', 'alpha_pct', 'max_dd_pct', 'composite_score'\n",
                    "]].copy()\n",
                    "df_scorecard.to_csv(os.path.join(base_dir, 'fund_scorecard.csv'), index=False)\n",
                    "df_scorecard.to_csv(os.path.join(base_dir, 'reports', 'fund_scorecard.csv'), index=False)\n",
                    "df_alpha_beta = df_metrics[['amfi_code', 'scheme_name', 'alpha_pct', 'beta', 'volatility_ann_pct']]\n",
                    "df_alpha_beta.to_csv(os.path.join(base_dir, 'alpha_beta.csv'), index=False)\n",
                    "df_alpha_beta.to_csv(os.path.join(base_dir, 'reports', 'alpha_beta.csv'), index=False)\n",
                    "print(\"Saved fund_scorecard.csv and alpha_beta.csv to root and reports directories.\")"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "### 8. Plot Benchmark Comparison Chart & Calculate Tracking Error"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Setup mapping and pivot close prices\n",
                    "benchmark_mapping = {\n",
                    "    'NIFTY 100 TRI': 'NIFTY100',\n",
                    "    'BSE 250 SmallCap TRI': 'BSE_SMALLCAP',\n",
                    "    'CRISIL Dynamic Gilt Index': 'CRISIL_GILT',\n",
                    "    'NIFTY Midcap 150 TRI': 'NIFTY_MIDCAP150',\n",
                    "    'CRISIL Short Term Bond Index': 'CRISIL_LIQUID',\n",
                    "    'NIFTY 500 TRI': 'NIFTY500',\n",
                    "    'CRISIL Liquid Fund AI Index': 'CRISIL_LIQUID',\n",
                    "    'NIFTY 50 TRI': 'NIFTY50',\n",
                    "    'NIFTY Midcap 50 TRI': 'NIFTY_MIDCAP150',\n",
                    "    'NIFTY Large Midcap 250 TRI': 'NIFTY500'\n",
                    "}\n",
                    "df_bench_pivot = df_bench.pivot(index='date', columns='index_name', values='close_value')\n",
                    "df_bench_ret_pivot = df_bench.pivot(index='date', columns='index_name', values='daily_return')\n",
                    "\n",
                    "# Get top 5 funds\n",
                    "top_5 = df_metrics.head(5)\n",
                    "dates_3yr = pd.date_range(start='2023-05-29', end='2026-05-29', freq='D')\n",
                    "\n",
                    "plt.figure(figsize=(12, 7))\n",
                    "\n",
                    "# Plot Benchmarks\n",
                    "nifty50_prices = df_bench_pivot['NIFTY50'].loc[dates_3yr]\n",
                    "nifty50_cum = (nifty50_prices / nifty50_prices.iloc[0]) * 100\n",
                    "plt.plot(nifty50_cum.index, nifty50_cum.values, label='Nifty 50 TRI (Benchmark)', color='#555555', linewidth=2.0, linestyle='--')\n",
                    "\n",
                    "nifty100_prices = df_bench_pivot['NIFTY100'].loc[dates_3yr]\n",
                    "nifty100_cum = (nifty100_prices / nifty100_prices.iloc[0]) * 100\n",
                    "plt.plot(nifty100_cum.index, nifty100_cum.values, label='Nifty 100 TRI (Benchmark)', color='#888888', linewidth=2.0, linestyle='-.')\n",
                    "\n",
                    "# Plot Top 5 funds\n",
                    "colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']\n",
                    "tracking_errors = []\n",
                    "\n",
                    "for idx, fund_row in top_5.iterrows():\n",
                    "    code = fund_row['amfi_code']\n",
                    "    name = fund_row['scheme_name']\n",
                    "    short_name = name.split(\" - \")[0]\n",
                    "    \n",
                    "    fund_nav = df_nav[(df_nav['amfi_code'] == code) & (df_nav['date'].isin(dates_3yr))].sort_values('date')\n",
                    "    \n",
                    "    nav_start = fund_nav['nav'].iloc[0]\n",
                    "    fund_cum = (fund_nav['nav'] / nav_start) * 100\n",
                    "    plt.plot(fund_nav['date'], fund_cum, label=f\"{short_name} (Rank {fund_row['rank']})\", color=colors[idx], linewidth=1.8)\n",
                    "    \n",
                    "    # Compute Tracking Error\n",
                    "    bench_col = benchmark_mapping.get(fund_row['benchmark'], 'NIFTY100')\n",
                    "    fund_ret = fund_nav['daily_return'].values[1:]\n",
                    "    bench_ret = df_bench_ret_pivot[bench_col].loc[fund_nav['date']].values[1:]\n",
                    "    \n",
                    "    te = np.std(fund_ret - bench_ret, ddof=1) * np.sqrt(252)\n",
                    "    tracking_errors.append({\n",
                    "        'scheme_name': name,\n",
                    "        'benchmark': fund_row['benchmark'],\n",
                    "        'tracking_error_pct': te * 100\n",
                    "    })\n",
                    "\n",
                    "plt.title(\"3-Year Cumulative Performance Comparison: Top 5 Funds vs Benchmarks (2023-2026)\", fontsize=13, fontweight='bold', pad=15)\n",
                    "plt.xlabel(\"Date\", fontsize=11, labelpad=10)\n",
                    "plt.ylabel(\"Normalized Value (Base = 100 on 2023-05-29)\", fontsize=11, labelpad=10)\n",
                    "plt.legend(loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#dddddd')\n",
                    "plt.tight_layout()\n",
                    "plt.savefig(os.path.join(base_dir, 'benchmark_comparison_chart.png'), dpi=300)\n",
                    "plt.show()\n",
                    "\n",
                    "print(\"Tracking Errors for Top 5 Funds:\")\n",
                    "display(pd.DataFrame(tracking_errors))"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    
    notebook_path = os.path.join(base_dir, 'notebooks', 'Performance_Analytics.ipynb')
    os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(notebook_content, f, indent=1)
    
    print(f"Jupyter notebook saved to {notebook_path}")
    print("Performance analytics complete!")

if __name__ == '__main__':
    run_performance_analytics()
