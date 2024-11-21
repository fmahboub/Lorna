import streamlit as st
import pandas as pd
# import plotly.express as px
import altair as alt


# DATA PRE-PROCESSING CODE --------------------------------------------------------------------

# Load MAIN TABLE TO CSV
CFMS_df = pd.read_csv('data/CashFlow Momentum Score- CMS-S&P 500 - Cash Flow Momentum Score (CMS)-S&P 500.csv', header=1)
# generate list of column names that are corresponding to the years
year_columns = [x for x in CFMS_df.columns if x.isnumeric()]
for col in year_columns:
    CFMS_df[col] = CFMS_df[col].apply(lambda x: round(x) if not pd.isna(x) else x)
# Create list of company names for using in drop-down menu
company_name_list = list(CFMS_df['Company Name'])
main_table_display_columns = [x for x in CFMS_df.columns if x not in year_columns]
main_table_display_columns.remove('Index Weight')

CCE_df = pd.read_csv('data/components/CashFlow Momentum Score- CMS-S&P 500 - Cash Conversion Efficency Normalized Score.csv', header=1)
EBITDA_df = pd.read_csv('data/components/CashFlow Momentum Score- CMS-S&P 500 - EBITDA Margin Normalized Score.csv', header=1)
FCF_df = pd.read_csv('data/components/CashFlow Momentum Score- CMS-S&P 500 - FCF Yield Normalized Score.csv', header=1)
OCFG_df = pd.read_csv('data/components/CashFlow Momentum Score- CMS-S&P 500 - Operating Cash Flow Growth Normalized Score.csv', header=1)
ROIC_df = pd.read_csv('data/components/CashFlow Momentum Score- CMS-S&P 500 - Return on Invested Capital Normalized Score.csv', header=1)
comp_table_names = ['CCE_df','EBITDA_df','FCF_df','OCFG_df','ROIC_df']

# APP CODE ------------------------------------------------------------------------------------
st.set_page_config(layout="wide")

# Create a navigation menu at the top
menu = st.radio("Navigate to:",
    ("Home", "Rankings", "About"),
    horizontal=True)  # This makes the radio buttons horizontal

# DISPLAY DIFFERENT PAGES BASED ON SELECTION
if menu == "Home":

    st.title("LORNA")
    st.write(
        "Compare Companies Using Cash Flow Momentum Score (CFMS)"
    )
    # CREATES DROPDOWN MENU FOR SELECTING COMPANIES
    selected_companies = st.multiselect("Select Companies to Compare", company_name_list, default=company_name_list[:3])
    # ONLY DISPLAY ANYTHING IF THE SELECTION HAS AT LEAST 1 COMPANY
    if len(selected_companies) > 0:
        temp_table = CFMS_df.loc[CFMS_df['Company Name'].isin(selected_companies)]
        # MAKE A COPY FOR TIMELINE VISUAL
        temp_timeline_table = temp_table.copy()
        temp_timeline_table = temp_timeline_table[['Company Name']+[x for x in temp_timeline_table.columns if x not in main_table_display_columns]].drop(columns='Index Weight')
        # FILTER temp_table TO ONLY CONTAIN APPROPRIATE COLUMNS
        temp_table = temp_table[main_table_display_columns]
        temp_table[main_table_display_columns[2:]] = temp_table[main_table_display_columns[2:]].fillna(0).astype(int)
        st.table(temp_table.reset_index(drop=True))
        # Create a bar chart from the 'Values' column
        chart_option = st.radio("Choose metric to display:",('TTM', 'Latest Fiscal Year', 'Latest Qtr'),horizontal =True)
        # CREATE BAR CHART WITH CUSTOM Y-AXIS RANGE
        chart = alt.Chart(temp_table).mark_bar().encode(
            x=alt.X('Company Name',title='Company',axis=alt.Axis(labelAngle=0)),
            y=alt.Y(chart_option, scale=alt.Scale(domain=[0, max(temp_table[chart_option])+5]), title='CFMS  '+chart_option))
        st.altair_chart(chart, use_container_width=True)
    # CREATE TEMP TABLE OF COMPONENTS FOR DISPLAY
    temp_comps_table = temp_table[main_table_display_columns[:2]].reset_index(drop=True)
    for table_name in comp_table_names:
        temp_comp_table = globals()[table_name]
        temp_comp_table = temp_comp_table.loc[temp_comp_table['Company Name'].isin(selected_companies)]
        temp_comp_table = temp_comp_table[main_table_display_columns[:2]+[chart_option]].rename(columns={chart_option:table_name[:-3]+' '+chart_option}).reset_index(drop=True)
        temp_comps_table = pd.merge(temp_comps_table, temp_comp_table, how='outer', on=['Company Name', 'Stock Symbol'])
    temp_comps_table[temp_comps_table.columns[2:]] = temp_comps_table[temp_comps_table.columns[2:]].fillna(0).astype(int)
    # MELT THE DATAFRAME TO GET IT INTO THE RIGHT FORMAT FOR ALTAIR
    df_melted = temp_comps_table.melt(
        id_vars=['Company Name', 'Stock Symbol'],
        value_vars=temp_comps_table.columns[2:],
        var_name='Metric',
        value_name='Value')

    # CREATE ALTAIR CHART WITH DODGED (side-by-side) BARS FOR EACH COMPONENT
    chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X('Company Name:N', title='Company',axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Value:Q', title='Normalized  Value'),
        color='Metric:N',
        xOffset='Metric:N',  # This creates the side-by-side effect
        tooltip=['Company Name', 'Stock Symbol', 'Metric', 'Value'])

    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)
    # PIVOT TIMELINE TABLE TO LONG FORMAT
    temp_timeline_table_long = temp_timeline_table.melt(id_vars=["Company Name"], var_name="Year", value_name="CFMS")
    # CREATE THE LINE CHART
    line_chart = (
        alt.Chart(temp_timeline_table_long)
        .mark_line()
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("CFMS:Q", title="CFMS"),
            color="Company Name:N",
            tooltip=["Company Name", "Year", "CFMS"],
        ).interactive())
    # DISPLAY THE CHART IN STREAMLIT
    st.altair_chart(line_chart, use_container_width=True)

elif menu == "Rankings":
    st.title("Rankings")
    # CHANGE THE COLUMN NAMES SO THAT THEY ARE MORE EXPLICIT
    chart_option_mapping = {'Index Weight':'S&P 500 Index Weight','TTM':'CFMS TTM','Latest Fiscal Year':'CFMS LFY'}
    ranking_table = CFMS_df.rename(columns = chart_option_mapping)
    # REMOVE THE COLUMNS FOR EACH YEAR CFMS
    ranking_table = ranking_table.loc[:,:'4 QTR Ago']
    ranking_table.insert(1,'Stock Symbol',ranking_table.pop('Stock Symbol'))
    numeric_cols = ranking_table.columns[3:]
    ranking_table[numeric_cols] = ranking_table[numeric_cols].apply(pd.to_numeric, errors='coerce')
    ranking_table = ranking_table.dropna(subset=['Company Name','Stock Symbol'])
    st.dataframe(ranking_table, use_container_width=True)

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
