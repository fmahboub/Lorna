import pandas as pd

CFMS_df = pd.read_csv('/workspaces/Lorna_0.1/data/CashFlow Momentum Score- CMS-S&P 500 - Cash Flow Momentum Score (CMS)-S&P 500.csv',header=1)
print("File loaded successfully.")
company_name_list = list(CFMS_df['Company Name'])
print(company_name_list)
