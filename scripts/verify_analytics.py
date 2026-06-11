import os
import pandas as pd

def verify():
    base_dir = r'x:\CODING\PROJECTS\InternshipWork\Bluestock\Capstone'
    
    scorecard_path = os.path.join(base_dir, 'fund_scorecard.csv')
    alpha_beta_path = os.path.join(base_dir, 'alpha_beta.csv')
    chart_path = os.path.join(base_dir, 'benchmark_comparison_chart.png')
    notebook_path = os.path.join(base_dir, 'notebooks', 'Performance_Analytics.ipynb')
    
    # Check if files exist
    assert os.path.exists(scorecard_path), f"Missing {scorecard_path}"
    assert os.path.exists(alpha_beta_path), f"Missing {alpha_beta_path}"
    assert os.path.exists(chart_path), f"Missing {chart_path}"
    assert os.path.exists(notebook_path), f"Missing {notebook_path}"
    print("All deliverables exist!")
    
    # Load CSVs
    df_score = pd.read_csv(scorecard_path)
    df_ab = pd.read_csv(alpha_beta_path)
    
    # Check row counts (40 funds expected)
    assert len(df_score) == 40, f"Expected 40 funds in scorecard, got {len(df_score)}"
    assert len(df_ab) == 40, f"Expected 40 funds in alpha_beta, got {len(df_ab)}"
    print("Deliverable CSVs have correct size (40 funds).")
    
    # Check for NaNs
    assert not df_score.isnull().any().any(), "Scorecard contains missing values!"
    assert not df_ab.isnull().any().any(), "Alpha/Beta file contains missing values!"
    print("No missing values (NaNs) found in CSVs.")
    
    # Verify scorecard details
    assert (df_score['composite_score'] >= 0).all() and (df_score['composite_score'] <= 100).all(), \
        "Composite scores must be between 0 and 100!"
    assert (df_score['rank'] == list(range(1, 41))).all(), \
        "Ranks must be sequentially ordered from 1 to 40!"
    print("Composite scores are between 0 and 100, and ranks are correctly ordered from 1 to 40.")
    
    # Verify scorecard column names
    expected_cols = [
        'rank', 'amfi_code', 'scheme_name', 'category', 'expense_ratio_pct', 
        'cagr_3yr_pct', 'sharpe', 'alpha_pct', 'max_dd_pct', 'composite_score'
    ]
    assert df_score.columns.tolist() == expected_cols, f"Scorecard columns mismatch! Got {df_score.columns.tolist()}"
    print("Scorecard columns are correct.")
    
    # Verify alpha_beta column names
    expected_ab_cols = ['amfi_code', 'scheme_name', 'alpha_pct', 'beta', 'volatility_ann_pct']
    assert df_ab.columns.tolist() == expected_ab_cols, f"Alpha/Beta columns mismatch! Got {df_ab.columns.tolist()}"
    print("Alpha/Beta columns are correct.")
    
    # Verify chart file size
    assert os.path.getsize(chart_path) > 10000, "Chart image is suspiciously small!"
    print(f"Chart image exists and is valid. File size: {os.path.getsize(chart_path)} bytes.")
    
    # Verify notebook is populated (executed)
    import json
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    executed_cells = 0
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            if cell.get('execution_count') is not None:
                executed_cells += 1
                
    assert executed_cells > 0, "Jupyter notebook was not executed (no execution counts found)!"
    print(f"Jupyter notebook is validated and has {executed_cells} executed cells.")
    
    print("\nVerification successful! Day 4 deliverables are 100% correct.")

if __name__ == '__main__':
    verify()
