import streamlit as st
import pandas as pd

# DATA PRE-PROCESSING CODE -----------------------------------------------------

# Load csv to pandas dataframe
CFMS_df = pd.read_csv('/workspaces/Lorna_0.1/data/CashFlow Momentum Score- CMS-S&P 500 - Cash Flow Momentum Score (CMS)-S&P 500.csv',header=1)
# generate list of column names that are corresponding to the years
year_columns = [x for x in CFMS_df.columns if x.isnumeric()]
for col in year_columns:
    CFMS_df[col] = CFMS_df[col].apply(lambda x: round(x) if not pd.isna(x) else x)
# Create list of company names for using in drop-down menu
company_name_list = list(CFMS_df['Company Name'])
main_table_display_columns = [x for x in CFMS_df.columns if x not in year_columns]

# APP CODE
st.set_page_config(layout="wide")

# Create a navigation menu at the top
menu = st.radio(
    "Navigate to:",
    ("Home", "About"),
    horizontal=True,  # This makes the radio buttons horizontal
)

# Display different pages based on selection
if menu == "Home":
    st.title("LORNA")
    st.write(
        "Compare Companies Using Cash Flow Momentum Score (CFMS)"
    )
    # Dropdown for preloaded companies
    selected_companies = st.multiselect("Select Companies to Compare", company_name_list, default=company_name_list[:3])
    if len(selected_companies) > 0:
        st.table(CFMS_df.loc[CFMS_df['Company Name'].isin(selected_companies)][main_table_display_columns])
elif menu == "About":
    st.title("About This App")
    st.write("""
        Lorna is a application that looks at how much cash publicly 
        isted companies are making, compares how fast their cash is growing, 
        and then uses that to give easy-to-understand tips about how those companies 
        might do when they report their earnings.""")
    st.markdown("<h1 style='font-size: 20px;'>1. The Problem</h1>", unsafe_allow_html=True)
    st.write('''Imagine you have lots of toys, and you want to pick the best ones to play with. But some toys look shiny on the outside, but when you play with them, they don't work well. The same happens with companies. Investors try to find the best companies to put their money into, but the numbers that show how well a company is doing can sometimes be tricky.
    Here’s why it's hard:
    Companies Trick the Numbers: Sometimes companies make their profits look bigger than they are by using tricks in the way they count money. So, the numbers might not really show how well the company is doing.
    Hard to Tell Real Cash from Fake Cash: Investors have trouble telling which companies are making real money (cash) and which ones are just saying they are making money on paper.
    Money Might Not Be Spent Well: Some companies don’t use their money very wisely, but you can't always see that with the regular numbers.
    Too Many Numbers to Look At: There are so many numbers to look at that it’s hard to know which ones matter. It can feel like trying to find one toy in a huge pile of toys!''')

    st.markdown("<h1 style='font-size: 20px;'>2. The Need</h1>", unsafe_allow_html=True)
    st.write('''Investors need a simpler way to figure out which companies are doing really well with their money. They need a system that helps them see the companies that are making real money and spending it wisely, without getting lost in all the confusing numbers.
                Here’s what investors need:
                Focus on Real Cash: Investors need to look at how much cash companies are really making, not just what their paper numbers say.
                Easy-to-Understand Scores: Instead of looking at lots of numbers, they need a simple score that tells them how well a company is doing.
                Helps Make Better Choices: Investors want to pick companies that will keep making money in the future, not companies that look good just for now.''')

    st.markdown("<h1 style='font-size: 20px;'>3. How is the Problem Solved?</h1>", unsafe_allow_html=True)
    st.write('''The Cash Flow Momentum Score (CFMS) is a special tool that helps investors see how well a company is doing with their money. It makes everything simpler by looking at the right numbers that show if a company is really making money and spending it wisely.
        Here’s what it does:
        Shows Real Money: The CFMS looks at how much real cash a company is making, instead of just paper profits.
        Simple and Clear: The CFMS gives a simple score that sums up all the important numbers, so investors don’t get confused by too much data.
        Focuses on Long-Term Success: The CFMS helps investors find companies that will keep making money and growing over time, not just in the short term.
        Helps Avoid Bad Choices: It also helps spot companies that might look good but aren't actually making real money or using their cash wisely.''')

    st.markdown("<h1 style='font-size: 20px;'>4. Who Can Benefit?</h1>", unsafe_allow_html=True)
    st.write('''Regular Investors: People who want an easy way to pick good companies without getting lost in lots of numbers.
    Big Investors: People who manage lots of money and need to find companies that are really good at making and using cash.
    Money Experts: Financial analysts who want a quick and easy way to see how healthy a company’s cash flow is.
    Fund Managers: People who manage lots of stocks and need to find the best companies for their portfolio.''')
