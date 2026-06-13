import os
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm

# -------------------------------------------------------------
# Streamlit Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Bluestock Mutual Fund Analytics & Risk Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling and premium feel (Bluestock colors: #414BEA and #F05537)
st.markdown("""
<style>
    :root {
        --primary-color: #414BEA;
        --secondary-color: #F05537;
        --background-color: #f8f9fa;
    }
    .main-title {
        color: #414BEA;
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #555555;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #414BEA;
        margin-bottom: 1rem;
    }
    .metric-card-alt {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #F05537;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #333333;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Database Helper functions (Cached)
# -------------------------------------------------------------
DB_PATH = r"x:\CODING\PROJECTS\InternshipWork\Bluestock\Capstone\data\db\bluestock_mf.db"

@st.cache_data
def get_connection_status():
    if os.path.exists(DB_PATH):
        return True
    return False

@st.cache_data
def load_dim_fund():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM dim_fund", conn)
    conn.close()
    return df

@st.cache_data
def load_fact_nav():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM fact_nav", conn)
    df['date'] = pd.to_datetime(df['date'])
    conn.close()
    return df

@st.cache_data
def load_fact_transactions():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM fact_transactions", conn)
    df['date'] = pd.to_datetime(df['date'])
    conn.close()
    return df

@st.cache_data
def load_fact_performance():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM fact_performance", conn)
    conn.close()
    return df

@st.cache_data
def load_fact_aum():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM fact_aum", conn)
    conn.close()
    return df

@st.cache_data
def load_fact_sip_industry():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM fact_sip_industry", conn)
    conn.close()
    return df

@st.cache_data
def load_fact_portfolio():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM fact_portfolio", conn)
    conn.close()
    return df

# Verify DB exists
if not get_connection_status():
    st.error(f"SQLite Database not found at `{DB_PATH}`. Please run `python run_pipeline.py` first to generate it.")
    st.stop()

# Load datasets
df_fund = load_dim_fund()
df_nav = load_fact_nav()
df_transactions = load_fact_transactions()
df_performance = load_fact_performance()
df_aum = load_fact_aum()
df_sip_industry = load_fact_sip_industry()
df_portfolio = load_fact_portfolio()

# -------------------------------------------------------------
# Sidebar Navigation
# -------------------------------------------------------------
st.sidebar.markdown("### Capstone Dashboard & Advanced Analytics")

pages = [
    "🏠 Executive & Industry Overview",
    "📈 Fund Performance & Scorecard",
    "👥 Investor Demographics & Cohorts",
    "🎲 Monte Carlo NAV Projection",
    "🕸️ Markowitz Portfolio Optimization"
]
selected_page = st.sidebar.radio("Navigate Pages", pages)

# -------------------------------------------------------------
# Page 1: Executive & Industry Overview
# -------------------------------------------------------------
if selected_page == "🏠 Executive & Industry Overview":
    st.markdown("<div class='main-title'>Mutual Fund Industry & Platform Overview</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>End-to-End Ingestion, Relational Schema Analytics, and Business Intelligence KPI Overview</div>", unsafe_allow_html=True)
    
    # KPIs row
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    # Get latest industry numbers
    latest_aum_row = df_aum.sort_values('date', ascending=False).iloc[0] if len(df_aum) > 0 else None
    latest_sip_row = df_sip_industry.sort_values('month', ascending=False).iloc[0] if len(df_sip_industry) > 0 else None
    
    aum_val = f"₹{latest_aum_row['aum_crore'] / 100000:.2f} Lakh Cr" if latest_aum_row is not None else "₹81.0 Lakh Cr"
    sip_val = f"₹{latest_sip_row['sip_inflow_crore']:.0f} Cr" if latest_sip_row is not None else "₹31,002 Cr"
    folio_val = f"{latest_sip_row['active_sip_accounts_crore']:.2f} Cr" if latest_sip_row is not None else "26.12 Cr"
    
    with kpi_col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Latest Industry AUM</div>
            <div class='metric-value'>{aum_val}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown(f"""
        <div class='metric-card-alt'>
            <div class='metric-label'>Monthly SIP Inflows</div>
            <div class='metric-value'>{sip_val}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Active SIP Accounts</div>
            <div class='metric-value'>{folio_val}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        st.markdown(f"""
        <div class='metric-card-alt'>
            <div class='metric-label'>Tracked Schemes</div>
            <div class='metric-value'>{len(df_fund)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Main figures row
    fig_col1, fig_col2 = st.columns(2)
    
    with fig_col1:
        st.markdown("### AMC Assets Under Management (AUM)")
        # Sum AUM by AMC for the latest date
        latest_date = df_aum['date'].max()
        df_aum_latest = df_aum[df_aum['date'] == latest_date].sort_values('aum_crore', ascending=False)
        fig_aum = px.bar(
            df_aum_latest,
            x='aum_crore',
            y='fund_house',
            orientation='h',
            title=f"AUM by Fund House (as of {latest_date})",
            labels={'aum_crore': 'AUM (₹ Crore)', 'fund_house': 'Fund House'},
            color_discrete_sequence=['#414BEA']
        )
        fig_aum.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
        st.plotly_chart(fig_aum, use_container_width=True)
        
    with fig_col2:
        st.markdown("### Industry SIP Inflow Trend")
        df_sip_trend = df_sip_industry.sort_values('month')
        fig_sip = px.line(
            df_sip_trend,
            x='month',
            y='sip_inflow_crore',
            title="Monthly Mutual Fund SIP Inflows (₹ Crore)",
            labels={'sip_inflow_crore': 'SIP Inflow (₹ Crore)', 'month': 'Month'},
            markers=True,
            color_discrete_sequence=['#F05537']
        )
        fig_sip.update_layout(height=400)
        st.plotly_chart(fig_sip, use_container_width=True)

# -------------------------------------------------------------
# Page 2: Fund Performance & Scorecard
# -------------------------------------------------------------
elif selected_page == "📈 Fund Performance & Scorecard":
    st.markdown("<div class='main-title'>Mutual Fund Performance Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Evaluate schemes based on returns, volatility, Sharpe, Sortino ratios, Alpha, Beta, and composite scores</div>", unsafe_allow_html=True)
    
    # Filter controls
    st.markdown("### Filter Controls")
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        f_house = st.multiselect("Select Fund House", options=df_fund['fund_house'].unique())
    with f_col2:
        f_category = st.multiselect("Select Category", options=df_fund['category'].unique())
    with f_col3:
        f_plan = st.selectbox("Select Plan Type", options=["All", "Direct", "Regular"])
        
    # Apply filters
    filtered_funds = df_fund.copy()
    if f_house:
        filtered_funds = filtered_funds[filtered_funds['fund_house'].isin(f_house)]
    if f_category:
        filtered_funds = filtered_funds[filtered_funds['category'].isin(f_category)]
    if f_plan != "All":
        filtered_funds = filtered_funds[filtered_funds['plan'].str.contains(f_plan, case=False, na=False)]
        
    # Merge with performance metrics
    df_perf_merged = filtered_funds.merge(df_performance, on='amfi_code')
    
    # Merge with composite scorecard (which is generated in reports/fund_scorecard.csv or computed)
    scorecard_path = r"x:\CODING\PROJECTS\InternshipWork\Bluestock\Capstone\fund_scorecard.csv"
    if os.path.exists(scorecard_path):
        df_scorecard = pd.read_csv(scorecard_path)
        # Drop redundant scheme name/category to avoid suffixes
        df_scorecard_subset = df_scorecard[['amfi_code', 'composite_score', 'rank']]
        df_perf_merged = df_perf_merged.merge(df_scorecard_subset, on='amfi_code', how='left')
        
    # Columns grid
    perf_col1, perf_col2 = st.columns([1, 1])
    
    with perf_col1:
        st.markdown("### Risk-Return Scatter Plot (3-Yr CAGR vs Volatility)")
        if not df_perf_merged.empty:
            fig_scatter = px.scatter(
                df_perf_merged,
                x='cagr_3yr_pct' if 'cagr_3yr_pct' in df_scorecard.columns else 'return_3yr',
                y='std_dev_ann_pct',
                size='composite_score' if 'composite_score' in df_perf_merged.columns else None,
                color='category',
                hover_name='scheme_name',
                title="3-Year Return vs Annualized Volatility",
                labels={'return_3yr': '3-Yr CAGR (%)', 'cagr_3yr_pct': '3-Yr CAGR (%)', 'std_dev_ann_pct': 'Annualized Volatility (%)'},
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_scatter.update_layout(height=450)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.warning("No data matches selected filters.")
            
    with perf_col2:
        st.markdown("### Interactive Fund Scorecard")
        if not df_perf_merged.empty:
            display_cols = ['rank', 'scheme_name', 'category', 'return_3yr', 'sharpe', 'alpha', 'max_dd', 'composite_score']
            display_cols = [c for c in display_cols if c in df_perf_merged.columns]
            
            # Formatting values
            df_display = df_perf_merged[display_cols].copy()
            if 'rank' in df_display.columns:
                df_display['rank'] = df_display['rank'].astype(int)
            df_display = df_display.sort_values('composite_score', ascending=False)
            
            st.dataframe(df_display, height=450, use_container_width=True)
        else:
            st.warning("No scorecard data to display.")
            
    # Selected Fund Details Section
    st.markdown("---")
    st.markdown("### Detailed NAV vs. Benchmark Comparison")
    selected_scheme = st.selectbox("Select a Scheme for NAV Analysis", options=df_perf_merged['scheme_name'].unique() if not df_perf_merged.empty else df_fund['scheme_name'].unique())
    
    if selected_scheme:
        sel_amfi = df_fund[df_fund['scheme_name'] == selected_scheme].iloc[0]['amfi_code']
        df_nav_scheme = df_nav[df_nav['amfi_code'] == sel_amfi].sort_values('date')
        
        # Load benchmark closing data
        benchmark_path = r"x:\CODING\PROJECTS\InternshipWork\Bluestock\Capstone\data\processed\10_benchmark_indices_clean.csv"
        if os.path.exists(benchmark_path):
            df_bench = pd.read_csv(benchmark_path)
            df_bench['date'] = pd.to_datetime(df_bench['date'])
            # Match benchmark index
            scheme_bench = df_fund[df_fund['scheme_name'] == selected_scheme].iloc[0]['benchmark']
            # Map clean benchmark names
            bench_map = {
                'Nifty 50 TRI': 'NIFTY50',
                'Nifty 50': 'NIFTY50',
                'Nifty 100 TRI': 'NIFTY100',
                'Nifty Midcap 150 TRI': 'NIFTY_MIDCAP_150',
                'BSE SmallCap TRI': 'BSE_SMALLCAP',
                'CRISIL Liquid Fund Index': 'CRISIL_LIQUID'
            }
            mapped_bench = bench_map.get(scheme_bench, 'NIFTY100')
            df_bench_filtered = df_bench[df_bench['index_name'] == mapped_bench].sort_values('date')
            
            # Merge NAV & Benchmark for comparison
            df_comparison = pd.merge(df_nav_scheme, df_bench_filtered, on='date', how='inner')
            
            # Normalize NAV and Benchmark to 100 at start date
            if not df_comparison.empty:
                first_nav = df_comparison.iloc[0]['nav']
                first_bench = df_comparison.iloc[0]['close_value']
                df_comparison['Normalized Fund NAV'] = (df_comparison['nav'] / first_nav) * 100
                df_comparison['Normalized Benchmark'] = (df_comparison['close_value'] / first_bench) * 100
                
                fig_comp = go.Figure()
                fig_comp.add_trace(go.Scatter(x=df_comparison['date'], y=df_comparison['Normalized Fund NAV'], name=f"Fund: {selected_scheme.split(' - ')[0]}", line=dict(color='#414BEA', width=2)))
                fig_comp.add_trace(go.Scatter(x=df_comparison['date'], y=df_comparison['Normalized Benchmark'], name=f"Benchmark: {scheme_bench}", line=dict(color='#F05537', width=1.5, dash='dash')))
                fig_comp.update_layout(title="Normalized Cumulative Growth (Base 100)", xaxis_title="Date", yaxis_title="Normalized Value", height=450)
                st.plotly_chart(fig_comp, use_container_width=True)
            else:
                st.warning("No overlapping NAV and Benchmark data found.")

# -------------------------------------------------------------
# Page 3: Investor Demographics & Cohorts
# -------------------------------------------------------------
elif selected_page == "👥 Investor Demographics & Cohorts":
    st.markdown("<div class='main-title'>Investor Analytics & Cohort Retentions</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Demographic breakdown of 5,000 retail accounts, state contributions, and cohort signups</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Transaction Value by State")
        df_state = df_transactions.groupby('state')['amount'].sum().reset_index()
        df_state = df_state.sort_values('amount', ascending=False)
        fig_state = px.bar(
            df_state,
            x='state',
            y='amount',
            title="Total Inflow Volume by State",
            labels={'amount': 'Total Investment (₹)', 'state': 'State'},
            color_discrete_sequence=['#414BEA']
        )
        fig_state.update_layout(height=400)
        st.plotly_chart(fig_state, use_container_width=True)
        
    with col2:
        st.markdown("### Transaction Type Allocation")
        df_type = df_transactions.groupby('type')['amount'].sum().reset_index()
        fig_type = px.pie(
            df_type,
            names='type',
            values='amount',
            title="SIP vs Lumpsum vs Redemption Volume",
            color_discrete_sequence=['#414BEA', '#F05537', '#dddddd']
        )
        fig_type.update_layout(height=400)
        st.plotly_chart(fig_type, use_container_width=True)
        
    # Cohorts Analysis Report
    st.markdown("---")
    st.markdown("### Investor Cohort Summary Table")
    cohort_path = r"x:\CODING\PROJECTS\InternshipWork\Bluestock\Capstone\reports\cohort_analysis_report.csv"
    if os.path.exists(cohort_path):
        df_cohort = pd.read_csv(cohort_path)
        # Format currency
        df_cohort['avg_sip_amount'] = df_cohort['avg_sip_amount'].map(lambda x: f"₹{x:,.2f}")
        df_cohort['total_invested_inr'] = df_cohort['total_invested_inr'].map(lambda x: f"₹{x:,.2f}")
        st.table(df_cohort)
    else:
        st.warning("Cohort analysis report not generated yet.")

# -------------------------------------------------------------
# Page 4: Monte Carlo NAV Projection
# -------------------------------------------------------------
elif selected_page == "🎲 Monte Carlo NAV Projection":
    st.markdown("<div class='main-title'>Monte Carlo NAV Growth Simulation</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Project mutual fund NAV values over a 5-year horizon based on Geometric Brownian Motion (GBM) with confidence intervals</div>", unsafe_allow_html=True)
    
    # Simulation input controls
    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        selected_scheme = st.selectbox("Select Mutual Fund", options=df_fund['scheme_name'].unique())
    with sim_col2:
        sim_years = st.slider("Simulation Duration (Years)", min_value=1, max_value=5, value=3)
    with sim_col3:
        num_sims = st.slider("Number of Simulation Runs", min_value=100, max_value=1000, value=500, step=100)
        
    # Run simulation button
    if st.button("Run Simulation", type="primary"):
        sel_amfi = df_fund[df_fund['scheme_name'] == selected_scheme].iloc[0]['amfi_code']
        fund_nav = df_nav[df_nav['amfi_code'] == sel_amfi].sort_values('date').copy()
        
        # Calculate daily returns
        fund_nav['returns'] = fund_nav['nav'].pct_change()
        daily_returns = fund_nav['returns'].dropna()
        
        if len(daily_returns) > 30:
            # Estimate GBM parameters
            mu = daily_returns.mean()
            sigma = daily_returns.std()
            
            # Annualized parameters
            ann_mu = mu * 252
            ann_std = sigma * np.sqrt(252)
            
            # Setup simulation time grids
            t_days = int(sim_years * 252)
            initial_nav = fund_nav.iloc[-1]['nav']
            
            # Matrix of random standard normal variables
            Z = np.random.normal(size=(t_days, num_sims))
            
            # Calculate simulated paths
            drift = mu - 0.5 * (sigma ** 2)
            sim_returns = drift + sigma * Z
            sim_paths = initial_nav * np.exp(np.cumsum(sim_returns, axis=0))
            
            # Prepend starting price
            sim_paths = np.vstack([np.full(num_sims, initial_nav), sim_paths])
            
            # Time axis mapping
            dates = pd.date_range(start=fund_nav.index[-1] if isinstance(fund_nav.index[-1], pd.Timestamp) else pd.to_datetime(fund_nav['date'].iloc[-1]), periods=t_days + 1, freq='B')
            
            # Aggregate stats
            p10 = np.percentile(sim_paths, 10, axis=1)
            p50 = np.percentile(sim_paths, 50, axis=1)
            p90 = np.percentile(sim_paths, 90, axis=1)
            
            # Plotly Chart
            fig_sim = go.Figure()
            
            # Plot first 15 paths for visualization
            for i in range(min(15, num_sims)):
                fig_sim.add_trace(go.Scatter(x=dates, y=sim_paths[:, i], mode='lines', line=dict(width=0.5, color='rgba(65, 75, 234, 0.15)'), showlegend=False))
                
            # Plot percentile bands
            fig_sim.add_trace(go.Scatter(x=dates, y=p90, line=dict(color='#F05537', width=1.5, dash='dash'), name="Optimistic (90th Percentile)"))
            fig_sim.add_trace(go.Scatter(x=dates, y=p50, line=dict(color='#414BEA', width=2), name="Median Projection (50th Percentile)"))
            fig_sim.add_trace(go.Scatter(x=dates, y=p10, line=dict(color='#888888', width=1.5, dash='dash'), name="Pessimistic (10th Percentile)"))
            
            fig_sim.update_layout(
                title=f"Monte Carlo NAV Projections for {selected_scheme.split(' - ')[0]}",
                xaxis_title="Simulation Date",
                yaxis_title="Projected NAV (₹)",
                height=500,
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )
            st.plotly_chart(fig_sim, use_container_width=True)
            
            # Stats breakdown
            st.markdown("### Simulation Outcomes Summary")
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            with stat_col1:
                st.metric(label="Current Final NAV", value=f"₹{initial_nav:.2f}")
                st.metric(label="Expected Annualized Return", value=f"{ann_mu*100:.2f}%")
            with stat_col2:
                st.metric(label="Median Projected NAV (50th)", value=f"₹{p50[-1]:.2f}", delta=f"{((p50[-1]/initial_nav)-1)*100:.2f}%")
                st.metric(label="Annualized Volatility (StdDev)", value=f"{ann_std*100:.2f}%")
            with stat_col3:
                st.metric(label="Optimistic NAV (90th)", value=f"₹{p90[-1]:.2f}")
                st.metric(label="Pessimistic NAV (10th)", value=f"₹{p10[-1]:.2f}")
        else:
            st.error("Insufficient historical NAV data points to estimate model volatility.")

# -------------------------------------------------------------
# Page 5: Markowitz Portfolio Optimization
# -------------------------------------------------------------
elif selected_page == "🕸️ Markowitz Portfolio Optimization":
    st.markdown("<div class='main-title'>Markowitz Mean-Variance Portfolio Optimization</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Build the Efficient Frontier using historical fund correlations and discover the Max Sharpe and Minimum Volatility allocations</div>", unsafe_allow_html=True)
    
    st.markdown("### Portfolio Asset Selection")
    st.info("Select exactly 5 funds from the list below to run the mean-variance optimization model:")
    
    # Multi-select 5 funds
    selected_optimize_funds = st.multiselect(
        "Select exactly 5 Funds",
        options=df_fund['scheme_name'].unique(),
        default=list(df_fund['scheme_name'].unique()[:5])
    )
    
    if len(selected_optimize_funds) == 5:
        # Load daily returns for selected funds
        fund_codes = df_fund[df_fund['scheme_name'].isin(selected_optimize_funds)]['amfi_code'].tolist()
        
        # Pull NAV history, pivot to align dates
        df_nav_opt = df_nav[df_nav['amfi_code'].isin(fund_codes)].copy()
        df_nav_pivot = df_nav_opt.pivot(index='date', columns='amfi_code', values='nav')
        
        # Calculate daily percentage returns
        df_returns_pivot = df_nav_pivot.pct_change().dropna()
        
        if len(df_returns_pivot) > 100:
            # Map codes to clean names
            code_name_map = {}
            for code in fund_codes:
                row = df_fund[df_fund['amfi_code'] == code].iloc[0]
                code_name_map[code] = row['scheme_name'].split(" - ")[0]
                
            df_returns_pivot.rename(columns=code_name_map, inplace=True)
            
            # Expected returns (annualized)
            exp_returns = df_returns_pivot.mean() * 252
            
            # Covariance matrix (annualized)
            cov_matrix = df_returns_pivot.cov() * 252
            
            # Run Monte Carlo Random Portfolios
            num_portfolios = 5000
            risk_free_rate = 0.065 # 6.5% risk-free rate proxy
            
            portfolio_returns = []
            portfolio_volatility = []
            portfolio_weights = []
            sharpe_ratios = []
            
            num_assets = 5
            
            for _ in range(num_portfolios):
                weights = np.random.random(num_assets)
                weights /= np.sum(weights) # Normalize to sum to 1
                
                # Portfolio Return: sum(w_i * R_i)
                p_ret = np.dot(weights, exp_returns)
                
                # Portfolio Volatility: sqrt(w^T * Cov * w)
                p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                
                # Sharpe Ratio
                p_sharpe = (p_ret - risk_free_rate) / p_vol
                
                portfolio_returns.append(p_ret)
                portfolio_volatility.append(p_vol)
                portfolio_weights.append(weights)
                sharpe_ratios.append(p_sharpe)
                
            # Convert arrays to numpy
            portfolio_returns = np.array(portfolio_returns)
            portfolio_volatility = np.array(portfolio_volatility)
            sharpe_ratios = np.array(sharpe_ratios)
            portfolio_weights = np.array(portfolio_weights)
            
            # Identify optimal portfolios
            max_sharpe_idx = np.argmax(sharpe_ratios)
            min_vol_idx = np.argmin(portfolio_volatility)
            
            best_sharpe_weights = portfolio_weights[max_sharpe_idx]
            min_vol_weights = portfolio_weights[min_vol_idx]
            
            # Plot the Efficient Frontier
            fig_frontier = go.Figure()
            fig_frontier.add_trace(go.Scatter(
                x=portfolio_volatility,
                y=portfolio_returns,
                mode='markers',
                marker=dict(
                    color=sharpe_ratios,
                    colorscale='Bluered',
                    showscale=True,
                    colorbar=dict(title="Sharpe Ratio")
                ),
                text=[f"Sharpe: {sr:.2f}" for sr in sharpe_ratios],
                name="Simulated Portfolios"
            ))
            
            # Highlight Optimal Portfolios
            fig_frontier.add_trace(go.Scatter(
                x=[portfolio_volatility[max_sharpe_idx]],
                y=[portfolio_returns[max_sharpe_idx]],
                mode='markers',
                marker=dict(color='yellow', size=15, symbol='star'),
                name="Maximum Sharpe Portfolio"
            ))
            
            fig_frontier.add_trace(go.Scatter(
                x=[portfolio_volatility[min_vol_idx]],
                y=[portfolio_returns[min_vol_idx]],
                mode='markers',
                marker=dict(color='green', size=15, symbol='star'),
                name="Minimum Volatility Portfolio"
            ))
            
            fig_frontier.update_layout(
                title="Markowitz Efficient Frontier & Simulated Portfolios",
                xaxis_title="Annualized Volatility (Risk)",
                yaxis_title="Expected Annual Return",
                height=500
            )
            st.plotly_chart(fig_frontier, use_container_width=True)
            
            # Show Optimal Allocations Side by Side
            opt_col1, opt_col2 = st.columns(2)
            
            with opt_col1:
                st.markdown("#### 🌟 Maximum Sharpe Portfolio")
                st.markdown(f"**Expected Annual Return**: {portfolio_returns[max_sharpe_idx]*100:.2f}%")
                st.markdown(f"**Annual Volatility**: {portfolio_volatility[max_sharpe_idx]*100:.2f}%")
                st.markdown(f"**Max Sharpe Ratio**: {sharpe_ratios[max_sharpe_idx]:.2f}")
                
                # Allocation DataFrame
                df_alloc_sharpe = pd.DataFrame({
                    'Fund Name': df_returns_pivot.columns,
                    'Optimal Weight': best_sharpe_weights * 100
                })
                df_alloc_sharpe['Optimal Weight'] = df_alloc_sharpe['Optimal Weight'].map(lambda x: f"{x:.2f}%")
                st.dataframe(df_alloc_sharpe, use_container_width=True)
                
            with opt_col2:
                st.markdown("#### 🛡️ Minimum Volatility Portfolio")
                st.markdown(f"**Expected Annual Return**: {portfolio_returns[min_vol_idx]*100:.2f}%")
                st.markdown(f"**Annual Volatility**: {portfolio_volatility[min_vol_idx]*100:.2f}%")
                st.markdown(f"**Sharpe Ratio**: {sharpe_ratios[min_vol_idx]:.2f}")
                
                # Allocation DataFrame
                df_alloc_vol = pd.DataFrame({
                    'Fund Name': df_returns_pivot.columns,
                    'Optimal Weight': min_vol_weights * 100
                })
                df_alloc_vol['Optimal Weight'] = df_alloc_vol['Optimal Weight'].map(lambda x: f"{x:.2f}%")
                st.dataframe(df_alloc_vol, use_container_width=True)
        else:
            st.error("Insufficient overlapping NAV history for selected portfolio assets.")
    else:
        st.warning("Please select exactly 5 mutual fund schemes to run the mean-variance optimization model.")
