-- queries.sql
-- 10 Analytical SQL Queries for Bluestock Mutual Fund Analytics Platform

-- 1. Top 5 Fund Houses by Total AUM in the Latest Quarter
SELECT fund_house, date, aum_crore 
FROM fact_aum 
WHERE date = (SELECT MAX(date) FROM fact_aum)
ORDER BY aum_crore DESC 
LIMIT 5;

-- 2. Monthly Average NAV for HDFC Top 100 Direct (AMFI Code: 125497) in 2024
SELECT strftime('%m', date) as month_num, AVG(nav) as average_nav
FROM fact_nav
WHERE amfi_code = '125497' AND date LIKE '2024%'
GROUP BY month_num
ORDER BY month_num;

-- 3. Industry-Wide SIP Inflows and YoY Growth
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM fact_sip_industry
ORDER BY month DESC
LIMIT 6;

-- 4. Investor Transaction Volume by State (in Crores)
SELECT state, COUNT(*) as transaction_count, SUM(amount)/10000000.0 as total_amount_crore
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_crore DESC;

-- 5. Funds with a Low Expense Ratio Less than 1%
SELECT amfi_code, fund_house, scheme_name, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC
LIMIT 5;

-- 6. Top 5 Sectors with Highest Portfolio Weight Across All Funds
SELECT sector, ROUND(AVG(weight_pct), 2) as avg_weight_pct
FROM fact_portfolio
GROUP BY sector
ORDER BY avg_weight_pct DESC
LIMIT 5;

-- 7. Investor KYC Status Distribution and Transaction Volumes
SELECT kyc_status, COUNT(DISTINCT investor_id) as investor_count, SUM(amount)/10000000.0 as total_amount_crore
FROM fact_transactions
GROUP BY kyc_status;

-- 8. Monthly Transaction Type Distribution (Last 12 Months)
SELECT strftime('%Y-%m', date) as month, type, COUNT(*) as tx_count, SUM(amount)/10000000.0 as amount_crore
FROM fact_transactions
GROUP BY month, type
ORDER BY month DESC, type ASC
LIMIT 12;

-- 9. Best 3-Year CAGR Funds with Risk Profiles
SELECT f.amfi_code, f.scheme_name, f.risk_category, p.return_3yr
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY p.return_3yr DESC
LIMIT 5;

-- 10. 30-Day Moving Average NAV of SBI Bluechip (AMFI Code: 119551) in Jan-Mar 2024
SELECT date, nav, 
       ROUND(AVG(nav) OVER (ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW), 2) as moving_avg_30d
FROM fact_nav
WHERE amfi_code = '119551' AND date BETWEEN '2024-01-01' AND '2024-03-31'
ORDER BY date
LIMIT 10;
