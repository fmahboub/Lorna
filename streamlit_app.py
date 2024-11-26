import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
import datetime
import pytz
import altair as alt


# DATA LOADING SAVING AND PRE-PROCESSING CODE --------------------------------------------------------------------

# LOAD TIME STAMP TO CHECK IF WE NEED AN API CALL
file_name = "data/data_timestamp.txt"
# Open the file in read mode
with open(file_name, "r") as file:
    last_timestamp = file.read()
last_timestamp_date = last_timestamp.split('_')[0]
last_timestamp_time= last_timestamp.split('_')[1]

est = pytz.timezone("US/Eastern")
current_timestamp = datetime.datetime.now(est).strftime("%Y-%m-%d_%H-%M-%S")
current_timestamp_date = current_timestamp.split('_')[0]
current_timestamp_time= current_timestamp.split('_')[1]

# COMPARE DATES OF PREVIOUS AND CURRENT TIMESTAMPS AND CALL API IF THE DATE HAS INCREASED AND IT'S PASSED 12 NOON 
if current_timestamp_date > last_timestamp_date and current_timestamp_time.split('-')[0]>'12':
    try:
        # AUTHENTICATE WITH GOOGLE SHEETS
        gc = gspread.service_account(filename='Google Cloud/blissful-flame-442915-s2-7a643e50638f.json')
    except:
        # Load credentials from Streamlit secrets
        credentials_json = st.secrets["google_cloud"]["credentials"]
        credentials_dict = json.loads(credentials_json)

        # Authenticate using the credentials
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)

        # Connect to Google Sheets
        gc = gspread.authorize(credentials)
    # OPEN THE MAIN SHEET
    CFMS_spreadsheet = gc.open("CashFlow Momentum Score (CFMS)- US & Canada Stocks")
    CFMS_df = pd.DataFrame(CFMS_spreadsheet.worksheet("CashFlow Momentum Score -US & Canada Stocks").get_all_records()).replace({'None': np.nan})
    # DROP COMPANY NAME DUPLICATES
    CFMS_df = CFMS_df.drop_duplicates(subset='Company Name').reset_index(drop=True)

    # LOAD COMPONENT TABLES
    CCE_df = pd.DataFrame(CFMS_spreadsheet.worksheet("Cash Flow Efficiency Normalized Score").get_all_records())\
                                                            .replace({'None': np.nan}).replace({'': np.nan}).drop_duplicates(subset='Company Name').reset_index(drop=True)
    EBITDA_df = pd.DataFrame(CFMS_spreadsheet.worksheet("EBITDA Margin Normalized Score").get_all_records())\
                                                            .replace({'None': np.nan}).replace({'': np.nan}).drop_duplicates(subset='Company Name').reset_index(drop=True)
    FCF_df = pd.DataFrame(CFMS_spreadsheet.worksheet("FCF Yield Normalized Score").get_all_records())\
                                                            .replace({'None': np.nan}).replace({'': np.nan}).drop_duplicates(subset='Company Name').reset_index(drop=True)
    OCFG_df = pd.DataFrame(CFMS_spreadsheet.worksheet("Operating Cash Flow Growth Normalized Score").get_all_records())\
                                                            .replace({'None': np.nan}).replace({'': np.nan}).drop_duplicates(subset='Company Name').reset_index(drop=True)
    ROIC_df = pd.DataFrame(CFMS_spreadsheet.worksheet("ROIC Score").get_all_records())\
                                                            .replace({'None': np.nan}).replace({'': np.nan}).drop_duplicates(subset='Company Name').reset_index(drop=True)

    CFMS_df.to_csv('data/CashFlow Momentum Score -US & Canada Stocks.csv',index=False)
    CCE_df.to_csv('data/components/Cash Flow Efficiency Normalized Score.csv',index=False)
    EBITDA_df.to_csv('data/components/EBITDA Margin Normalized Score.csv',index=False)
    FCF_df.to_csv('data/components/FCF Yield Normalized Score.csv',index=False)
    OCFG_df.to_csv('data/components/Operating Cash Flow Growth Normalized Score.csv',index=False)
    ROIC_df.to_csv('data/components/ROIC Score.csv',index=False)

    # GET THE TIMESTAMP OF CURRENT TIME AND DATE TO TRACK LAST DATA SAVE
    # SAVE CURRENT TIMESTAMP IN DATA DIRECTORY
    file_name = "data/data_timestamp.txt"
    # Save the file
    with open(file_name, "w") as file:
        file.write(current_timestamp)
else:
    CFMS_df = pd.read_csv('data/CashFlow Momentum Score -US & Canada Stocks.csv')
    CCE_df = pd.read_csv('data/components/Cash Flow Efficiency Normalized Score.csv')
    EBITDA_df = pd.read_csv('data/components/EBITDA Margin Normalized Score.csv')
    FCF_df = pd.read_csv('data/components/FCF Yield Normalized Score.csv')
    OCFG_df = pd.read_csv('data/components/Operating Cash Flow Growth Normalized Score.csv')
    ROIC_df = pd.read_csv('data/components/ROIC Score.csv')

# GENERATE LIST OF COLUMN NAMES THAT ARE CORRESPONDING TO THE YEARS
year_columns = [x for x in CFMS_df.columns if x.isnumeric()]
non_score_columns = list(CFMS_df.columns)[:list(CFMS_df.columns).index('Stock Symbol')+1]
score_columns = [x for x in CFMS_df.columns if x not in non_score_columns]
CFMS_df[score_columns] = CFMS_df[score_columns].astype(pd.Int64Dtype())
# CREATE LIST OF COMPANY NAMES FOR USING IN DROP-DOWN MENU
company_name_list = list(CFMS_df['Company Name'])
main_table_display_columns = [x for x in CFMS_df.columns if x not in year_columns]
comp_table_names = ['CCE_df','EBITDA_df','FCF_df','OCFG_df','ROIC_df']
# CONVERT SCORE COLUMNS TO INTS FOR EACH TABLE ABOVE
for table_name in comp_table_names:
    globals()[table_name][score_columns] = globals()[table_name][score_columns].astype(pd.Int64Dtype())

# APP CODE ------------------------------------------------------------------------------------
st.set_page_config(layout="wide")

# CREATE A NAVIGATION MENU AT THE TOP
menu = st.radio("Navigate to:",
    ("Home", "Rankings", "About"),
    horizontal=True)  # This makes the radio buttons horizontal
# DISPLAY THE LOGO
st.image('images/Lorna Logo.png',width=120)
# DISPLAY DIFFERENT PAGES BASED ON SELECTION
if menu == "Home":
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
        temp_timeline_table = temp_timeline_table[['Company Name']+[x for x in temp_timeline_table.columns if x in year_columns]]
        # FILTER temp_table TO ONLY CONTAIN APPROPRIATE COLUMNS
        temp_table = temp_table[main_table_display_columns]
        st.table(temp_table.reset_index(drop=True))
        # Create a bar chart from the 'Values' column
        chart_option = st.radio("Choose metric to display:",('Trailing Twelve Months (TTM) CFMS', 'Year-to-Date (YTD) CFMS', 'Latest Reported Quarter CFMS',),horizontal =True)
        # CREATE BAR CHART WITH CUSTOM Y-AXIS RANGE
        chart = alt.Chart(temp_table).mark_bar().encode(
            x=alt.X('Company Name',title='Company',axis=alt.Axis(labelAngle=0)),
            y=alt.Y(chart_option, scale=alt.Scale(domain=[0, max(temp_table[chart_option])+5]), title='CFMS  '+chart_option))
        st.altair_chart(chart, use_container_width=True)

        # CREATE TEMP TABLE OF COMPONENTS FOR DISPLAY
        temp_comps_table = temp_table[non_score_columns].reset_index(drop=True)
        for table_name in comp_table_names:
            temp_comp_table = globals()[table_name]
            temp_comp_table = temp_comp_table.loc[temp_comp_table['Company Name'].isin(selected_companies)]
            temp_comp_table = temp_comp_table[non_score_columns+[chart_option]].rename(columns={chart_option:table_name[:-3]+' '+chart_option}).reset_index(drop=True)
            temp_comps_table = pd.merge(temp_comps_table, temp_comp_table, how='outer', on=non_score_columns)
        temp_comps_table[temp_comps_table.columns[len(non_score_columns):]] = temp_comps_table[temp_comps_table.columns[len(non_score_columns):]].fillna(0).astype(int)

        # MELT THE DATAFRAME TO GET IT INTO THE RIGHT FORMAT FOR ALTAIR
        df_melted = temp_comps_table.melt(
            id_vars=['Company Name', 'Stock Symbol'],
            value_vars=temp_comps_table.columns[len(non_score_columns):],
            var_name='Metric',
            value_name='Value')

        # CREATE ALTAIR CHART WITH DODGED (side-by-side) BARS FOR EACH COMPONENT
        comp_bar_chart = alt.Chart(df_melted).mark_bar().encode(
            x=alt.X('Company Name:N', title='Company',axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Value:Q', title='Normalized  Value'),
            color='Metric:N',
            xOffset='Metric:N',  # This creates the side-by-side effect
            tooltip=['Company Name', 'Stock Symbol', 'Metric', 'Value'])

        # SET LEGEND ORIENTATION TO TOP
        comp_bar_chart = comp_bar_chart.configure_legend(orient='top', labelLimit=300)
        # DISPLAY THE CHART IN STREAMLIT
        st.altair_chart(comp_bar_chart, use_container_width=True)

        # PIVOT TIMELINE TABLE TO LONG FORMAT
        temp_timeline_table_long = temp_timeline_table.melt(id_vars=["Company Name"], var_name="Year", value_name="CFMS")
        # CREATE THE LINE CHART
        line_chart = (
            alt.Chart(temp_timeline_table_long)
            .mark_line()
            .encode(
                x=alt.X("Year:O", title="Year"),
                y=alt.Y("CFMS:Q", title="CFMS", scale=alt.Scale(domain=[round(temp_timeline_table_long.CFMS.min()-temp_timeline_table_long.CFMS.min()*.1),
                                                                        round(temp_timeline_table_long.CFMS.max()+temp_timeline_table_long.CFMS.max()*.1)])),
                color="Company Name:N",
                tooltip=["Company Name", "Year", "CFMS"],
            ).interactive())
        # DISPLAY THE CHART IN STREAMLIT
        line_chart = line_chart.configure_legend(orient='top')
        st.altair_chart(line_chart, use_container_width=True)

elif menu == "Rankings":
    st.title("Rankings")
    col1, col2 = st.columns(2)
    ranking_table = CFMS_df.copy().reset_index(drop=True)
    # SET UP FILTERS FOR RANKING PAGE
    sector_filter_options =  ['All'] + list(CFMS_df['Sector'].unique()) 
    with col1:
        sector_filter = st.selectbox('Select Sector:', options=sector_filter_options, index=0)
    if sector_filter != 'All':
        ranking_table = CFMS_df.copy().loc[CFMS_df.Sector==sector_filter].reset_index(drop=True)
    industry_filter_options =  ['All'] + list(ranking_table['Industry'].unique()) 
    with col2:
        industry_filter = st.selectbox('Select Industry:', options=industry_filter_options, index=0)
    if industry_filter != 'All':
        ranking_table = ranking_table.copy().loc[ranking_table.Industry==industry_filter].reset_index(drop=True)
    # REMOVE THE COLUMNS FOR EACH YEAR CFMS
    ranking_table = ranking_table.loc[:,:main_table_display_columns[-1]]
    ranking_table.insert(1,'Stock Symbol',ranking_table.pop('Stock Symbol'))
    st.dataframe(ranking_table, use_container_width=True, height=600)

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
