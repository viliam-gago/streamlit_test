import streamlit as st
import altair as alt
import pandas as pd
import sqlalchemy
import plotly.express as px

st.set_page_config(layout="wide")

query = '''
        SELECT
        	cbd.date,
            DATE_ADD(cbd.date, INTERVAL(-WEEKDAY(cbd.date)) DAY) week_monday,
        	cbd.country,
        	cbd.confirmed,
        	cbd.deaths,
        	cbd.recovered,
        	c.continent,
        	cc.iso3
        FROM covid19_basic_differences cbd
        LEFT JOIN countries c
        	on c.country = cbd.country
        LEFT JOIN country_codes cc
        	ON cc.country = cbd.country
        WHERE 1=1
        	AND confirmed > 0
        	AND deaths > 0
        	AND recovered > 0
        '''



## ----------------------------------------------------
@st.cache(allow_output_mutation=True)
def get_connection():
    user = 'student'
    password = "p7%40vw7MCatmnKjy7"
    conn_string = f"mysql+pymysql://{user}:{password}@data.engeto.com/data"
    return sqlalchemy.create_engine(conn_string)

@st.cache(allow_output_mutation=True)
def data_load(query):
    df = pd.read_sql(query, get_connection())
    return df


df = data_load(query)
df = df[~df['continent'].isna()]




## ----------------------------------------------------
st.sidebar.header('COVID DASHBOARD')
st.sidebar.header('Filters')

dates_options = list(df.date.unique())
filter_date = st.sidebar.slider('Date Range', min(dates_options), max(dates_options), (min(dates_options), max(dates_options)))

continent_options = list(df.continent.unique())
filter_continent = st.sidebar.multiselect('Select continent', continent_options)

if filter_continent:
    filtered_df = df[df['continent'].isin(filter_continent)]
    country_options = list(filtered_df.country.unique())
    filter_country = st.sidebar.multiselect('Select country', country_options)

    if filter_country:
        filtered_df = filtered_df[filtered_df['country'].isin(filter_country)]

else:
    country_options = list(df.country.unique())
    filter_country = st.sidebar.multiselect('Select country', country_options)
    if filter_country:
        filtered_df = df[df['country'].isin(filter_country)]
    else:
        filtered_df = df


filtered_df = filtered_df[ (filtered_df['date'] >= filter_date[0]) & (filtered_df['date'] <= filter_date[1]) ]

st.header('Covid data visualization')
filter_measure = st.selectbox('Select measure',('confirmed', 'deaths', 'recovered'))




# def create_linechart(df, filter_continent, filter_country, xaxis, measure):
#     if filter_country:
#         chrt = alt.Chart(df).mark_line(point=True).encode(
#             x=f'{xaxis}',
#             y=f'sum_measure'
#         )




## ----------------------------------------------------
chart1 = alt.Chart(filtered_df).mark_line().encode(
    x = 'date',
    y= 'sum_measure:Q'
).transform_aggregate(
    sum_measure = 'sum(confirmed)',
    groupby=['date']
).interactive()

st.altair_chart(chart1, use_container_width=True)
