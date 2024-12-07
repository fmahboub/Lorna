import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import numpy as np
import datetime
import pytz
import json
import altair as alt
from lorna_functions import *
from lorna_text_objects import *
import base64


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
current_timestamp_time = current_timestamp.split('_')[1]

# COMPARE DATES OF PREVIOUS AND CURRENT TIMESTAMPS AND CALL API IF THE DATE HAS INCREASED AND IT'S PASSED 12 NOON 
if current_timestamp_date > last_timestamp_date and int(current_timestamp_time.split('-')[0])>=12:
    try:
        # AUTHENTICATE WITH GOOGLE SHEETS
        gc = gspread.service_account(filename='Google Cloud/blissful-flame-442915-s2-7a643e50638f.json')
    except:
        # LOAD SECRETS
        credentials_dict = json.loads(st.secrets["google_cloud"]["credentials"])

        # AUTHENTICATE USING THE CREDENTIALS
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        # CONNECT TO GOOGLE SHEETS
        gc = gspread.authorize(credentials)

    # OPEN THE MAIN SHEET
    CFMS_spreadsheet = gc.open("CashFlow Momentum Score (CFMS)- US & Canada Stocks")
    CFMS_df = pd.DataFrame(CFMS_spreadsheet.worksheet("CashFlow Momentum Score -US & Canada Stocks").get_all_records()).replace({'None': np.nan})
    # DROP COMPANY NAME DUPLICATES
    CFMS_df = CFMS_df.drop_duplicates(subset='Company Name').reset_index(drop=True)

    # LOAD COMPONENT TABLES
    CFE_df = pd.DataFrame(CFMS_spreadsheet.worksheet("Cash Flow Efficiency Normalized Score").get_all_records())\
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
    CFE_df.to_csv('data/components/Cash Flow Efficiency Normalized Score.csv',index=False)
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
    last_timestamp = current_timestamp
else:
    CFMS_df = pd.read_csv('data/CashFlow Momentum Score -US & Canada Stocks.csv')
    CFE_df = pd.read_csv('data/components/Cash Flow Efficiency Normalized Score.csv')
    EBITDA_df = pd.read_csv('data/components/EBITDA Margin Normalized Score.csv')
    FCF_df = pd.read_csv('data/components/FCF Yield Normalized Score.csv')
    OCFG_df = pd.read_csv('data/components/Operating Cash Flow Growth Normalized Score.csv')
    ROIC_df = pd.read_csv('data/components/ROIC Score.csv')

# GENERATE LIST OF COLUMN NAMES THAT ARE CORRESPONDING TO THE YEARS
year_columns = [x for x in CFMS_df.columns if x.isnumeric()]
non_score_columns = list(CFMS_df.columns)[:list(CFMS_df.columns).index('Stock Symbol')+1]
score_columns = [x for x in CFMS_df.columns if x not in non_score_columns]
# ENSURE SCORE COLUMNS ARE INT DTYPE
CFMS_df[score_columns] = CFMS_df[score_columns].astype(pd.Int64Dtype())
# ADD INVESTOR RATING COLUMN TO CFMS_df AFTER 'Stock Symbol' COLUMN
rating_col_num = list(CFMS_df.columns).index('Stock Symbol') + 1
CFMS_df.insert(rating_col_num, 'Cash Flow Investor Rating',CFMS_df['Trailing Twelve Months (TTM) CFMS'].apply(lambda x: cfms_to_rating(x)))
# CREATE LIST OF COMPANY NAMES FOR USING IN DROP-DOWN MENU
company_name_list = list(CFMS_df['Company Name'])
main_table_display_columns = [x for x in CFMS_df.columns if x not in year_columns]
comp_table_names = ['CFE_df','EBITDA_df','FCF_df','OCFG_df','ROIC_df']
# CONVERT SCORE COLUMNS TO INTS FOR EACH TABLE ABOVE
for table_name in comp_table_names:
    globals()[table_name][score_columns] = globals()[table_name][score_columns].astype(pd.Int64Dtype())

# APP CODE ------------------------------------------------------------------------------------
st.set_page_config(layout="wide")

if 'landing_page' not in st.session_state:
    st.session_state.landing_page = True

if st.session_state.landing_page:
    # PLACE LOGO
    col1, col2, col3 = st.columns([4.5, 1, 4.5])  # Adjust widths for centering
    with col2:
        # Display the image in the center column
        st.image('images/Lorna Logo.png', use_container_width=True)

    # HEADER CENTERED AND STYLED TO ADAPT TO THEME
    st.markdown("""
    <style>
    /* Explicit selectors for theme detection */
    .stApp[data-theme='light'] .theme-subheader {
        color: black !important;
    }
    .stApp[data-theme='dark'] .theme-subheader {
        color: white !important;
    }
    </style>
    <div class="centered">
        <h2 style="text-align: center; color: darkorange;">Discover Winning Stocks Easily</h2>
        <h2 class="theme-subheader" style="text-align: center; font-size: 400%;">Cash Flow Momentum Score</h2>
        <div style="text-align: center; color: gray; font-size: 120%;">Cash Flow Insights for Smarter Investments</div>
    </div>
    """, 
    unsafe_allow_html=True)

    # BUTTON FORMATTING
    st.markdown("""
        <style>
        .centered-button {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }
        .stButton {
            width: auto !important;
            display: flex !important;
            justify-content: center !important;
        }
        .stButton button {
            background-color: #FF5733;  /* Orange color */
            color: black;               /* Text color */
            border: none;
            padding: 10px 20px;
            text-align: center;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);  /* Optional shadow */
        }
        .stButton button:hover {
            background-color: #FF3D00; /* Darker orange on hover */
        }
        </style>
    """, unsafe_allow_html=True)

    # Centering the button by using a div class and making it a part of the layout
    st.markdown('<div class="centered-button">', unsafe_allow_html=True)

    if st.button("&#9654; Try it out"):
        st.session_state.landing_page = False
        st.rerun()   

    # Closing the div to center the button
    st.markdown('</div>', unsafe_allow_html=True)
    
    # LANDING PAGE INFO MENU
    # Create columns for layout with the middle column being wider
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        # Align the radio horizontally in the middle
        options = ["Why Lorna?", "CFMS Explained", "Methodology", "Time Periods"]
        selected_option = st.selectbox("", options)
        # Using HTML to center the header
        st.markdown(f"<h1 style='text-align: center;'>{selected_option}</h1>", unsafe_allow_html=True)
        # st.write(landing_content_dict[selected_option])
        st.markdown(landing_content_dict[selected_option], unsafe_allow_html=True)

    # GIF TEST
    # col1, col2, col3 = st.columns([0.25, 1, 0.25])
    # with col2:
    #     st.write('')
    #     st.image('images/Landing Page Loop.gif', use_container_width='auto')
    # st.image('https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExc2VpdTllbDllOG04MHhia3dhd3h2cnlkamJobDZtdXZmODBnN3AzdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/VMBcS9qLM2uXK/giphy.gif', width=110)


if not st.session_state.landing_page:

    # Create two columns: one for the logo, one for the radio buttons
    col1, col2 = st.columns([1, 9])  # Adjust column ratios as needed

    with col1:
        st.image('images/Lorna Logo.png', width=110)

    with col2:
        menu = st.radio("Navigate to:",
                        ("Compare", "Screener", "Terminology", "About"),
                        horizontal=True)
    # DISPLAY DIFFERENT PAGES BASED ON SELECTION
    if menu == "Compare":
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
            temp_table = temp_table[main_table_display_columns].reset_index(drop=True)
            # CUSTOM CSS FOR TRANSPARENT BACKGROUND AND ADAPTIVE HEADER COLOR
            table_style = """
                <style>
                    .stTable thead th {
                        background-color: rgba(169, 169, 169, 0.1);  /* Light gray background for header */
                        color: currentColor;                          /* Adaptive header text color */
                        font-weight: bold;                            /* Bold header text */
                    }
                    .stTable td {
                        background-color: rgba(0, 0, 0, 0);         /* Fully transparent background for cells */
                        color: inherit;                               /* Inherit text color from parent (light/dark mode) */
                    }
                </style>
            """
            # Inject the custom CSS
            st.markdown(table_style, unsafe_allow_html=True)
            # DISPLAY MAIN TABLE
            st.table(temp_table)
            # CREATE A BAR CHART FROM THE 'VALUES' COLUMN
            chart_option = st.radio("Choose metric to display:",('Trailing Twelve Months (TTM) CFMS', 'Year-to-Date (YTD) CFMS', 'Latest Reported Quarter CFMS',),horizontal =True)
            # CREATE BAR CHART WITH CUSTOM Y-AXIS RANGE
                # FIND COLS WITH NULL VALUES AND DEPENDING ON THE SELECTION FROM chart_option REMOVE ANY ROW WITH NULLS
            temp_table_null_cols = temp_table.columns[temp_table.isnull().any()].tolist()
            if chart_option in temp_table_null_cols:
                temp_chart_table = temp_table.copy()[~temp_table.isin(['<NA>', 'NA', 'None']).any(axis=1)].dropna().reset_index(drop=True)
            else:
                temp_chart_table = temp_table.copy()
            chart = alt.Chart(temp_chart_table).mark_bar().encode(
                x=alt.X('Company Name',title='Company',axis=alt.Axis(labelAngle=0)),
                y=alt.Y(chart_option, scale=alt.Scale(domain=[0, max(temp_chart_table[chart_option])+5]), title='CFMS  '+chart_option))
            st.altair_chart(chart, use_container_width=True)

            # CREATE TEMP TABLE OF COMPONENTS FOR DISPLAY
            temp_comps_table = temp_table[non_score_columns].reset_index(drop=True)
            temp_comps_table = temp_comps_table[~temp_comps_table.isin(['<NA>', 'NA', 'None']).any(axis=1)]
            comps_table_name_map = {'FCF':'FCF Yield','EBITDA':'EBITDA Margin'}
            for table_name in comp_table_names:
                temp_comp_table = globals()[table_name]
                temp_comp_table = temp_comp_table.loc[temp_comp_table['Company Name'].isin(selected_companies)]
                temp_comp_table = temp_comp_table[non_score_columns+[chart_option]].rename(columns={chart_option:table_name[:-3]+' '+chart_option}).reset_index(drop=True)
                temp_comps_table = pd.merge(temp_comps_table, temp_comp_table, how='outer', on=non_score_columns)
            temp_comps_table[temp_comps_table.columns[len(non_score_columns):]] = temp_comps_table[temp_comps_table.columns[len(non_score_columns):]].fillna(0).astype(int)
            # ENSURE COLUMNS HAVE FULL NAMES BASED ON THE comps_table_name_map
            temp_comps_table.columns = [x.replace(x.split()[0],comps_table_name_map[x.split()[0]]) if x.split()[0] in comps_table_name_map.keys() else x for x in temp_comps_table.columns]
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

    elif menu == "Screener":
        st.title("Screener")
        col1, col2, col3 = st.columns([1, 1, 1])
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
        rating_filter_options =  ['All'] + list(ranking_table.dropna()['Cash Flow Investor Rating'].unique()) 
        with col3:
            rating_filter = st.selectbox('Select Investor Rating:', options=rating_filter_options, index=0)
        if rating_filter != 'All':
            ranking_table = ranking_table.copy().loc[ranking_table['Cash Flow Investor Rating']==rating_filter].reset_index(drop=True)
        # REMOVE THE COLUMNS FOR EACH YEAR CFMS
        ranking_table = ranking_table.loc[:,:main_table_display_columns[-1]]
        ranking_table.insert(1,'Stock Symbol',ranking_table.pop('Stock Symbol'))
        st.dataframe(ranking_table, use_container_width=True, height=600)

    elif menu == "Terminology":
        # SET UP THE PAGE TITLE
        st.title("Terminology")

        # Define sections of terminology
        st.header("Metrics")
        # st.subheader("Definition, Rationale, and Description")

        # Display metrics with headers and formatting
        for metric in metrics_data:
            st.markdown(f"{metric['Metric']}")
            st.markdown(f"- **Definition:** {metric['Definition']}")
            st.markdown(f"- **Rationale:** {metric['Rationale']}")
            st.markdown(f"- **Description:** {metric['Description']}")
            st.write("---")

    elif menu == "About":
        # Center the title using HTML and CSS
        st.markdown("<h1 style='text-align: center;'>About Us</h1>", unsafe_allow_html=True)
        # Add padding or spacing around the content
        # st.markdown("<div style='padding: 20px;'>", unsafe_allow_html=True)

        # Section 1: The Problem
        st.header("The Problem")
        st.write(
            """
            Investors often face challenges in identifying the best companies to invest in. While financial reports may look promising, they can be misleading due to:
            - **Accounting Tricks**: Inflated profits that don't reflect reality.
            - **Confusing Numbers**: Difficulty distinguishing real cash flow from paper profits.
            - **Inefficient Spending**: Hidden misuse of funds.
            - **Information Overload**: Too many metrics make decision-making overwhelming.
            """)

        st.markdown("---")  # Horizontal line for separation

        # Section 2: The Need
        st.header("The Need")
        st.write(
            """
            Investors need a clear, reliable way to evaluate a company's financial health:
            - **Focus on Real Cash**: Highlighting actual earnings, not just accounting figures.
            - **Simplified Scoring**: Easy-to-understand metrics that cut through the noise.
            - **Long-Term Insights**: Tools to identify companies with sustainable growth potential.
            """)

        st.markdown("---")

        # Section 3: Our Solution
        st.header("Our Solution")
        st.write(
            """
            The **Cash Flow Momentum Score (CFMS)** simplifies investment decisions by focusing on what really matters:
            - **Real Money Insights**: Evaluates genuine cash flow over superficial profits.
            - **Clear Scoring System**: Condenses complex data into an easy-to-use score.
            - **Future-Focused**: Identifies companies with strong long-term potential.
            - **Risk Reduction**: Flags businesses with poor cash management or misleading numbers.
            """)

        st.markdown("---")

        # Section 4: Who Benefits
        st.header("Who Benefits?")
        st.write(
            """
            - **Individual Investors**: Simplifies stock selection for personal portfolios.
            - **Institutional Investors**: Enhances decision-making for large-scale investments.
            - **Financial Analysts**: Streamlines evaluation of a company’s cash flow health.
            - **Fund Managers**: Identifies top-performing companies for diversified portfolios.
            """)

    if menu != 'Home':
        # DISPLAY LATEST DATA REFRESH
        st.markdown(
        f"<span style='font-size: 14px; font-weight: bold;'>Last Data Refresh: </span> "
        f"<span style='font-size: 14px;'>{last_timestamp.split('_')[0].replace('-', '/')} "
        f"@ {last_timestamp.split('_')[1].replace('-', ':')}</span>", unsafe_allow_html=True)
        # DISPLAY LEGAL DISCLAIMER
        st.markdown("<h2 style='font-size: 13px;'>Legal Disclaimer</h2>", unsafe_allow_html=True)
        st.markdown('''<p style='font-size:11px;'>
        The data provided on the Lorna platform is compiled from publicly available sources, including SEC filings and other financial reports, to ensure accuracy and transparency. All ratings, metrics, and insights generated by the Cash Flow Momentum Score (CFMS) or other tools are for informational purposes only.
        Lorna is not a registered investment advisor, broker-dealer, or financial planning service. The information presented on our platform should not be interpreted as financial advice or as a recommendation to buy, sell, or hold any specific securities. Our platform solely reflects the outputs of our proprietary algorithmic model and is not tailored to your individual financial circumstances.
        Investors should independently verify all data and conduct their own due diligence before making any investment decisions. We strongly encourage you to consult with a licensed financial advisor or other qualified professional regarding your financial situation and objectives.
        Lorna and its affiliates expressly disclaim any and all liability for any losses or damages arising from reliance on the information provided on this platform. By using Lorna, you acknowledge and agree to these terms.
        </p>''', unsafe_allow_html=True)
