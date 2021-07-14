import streamlit as st
import altair as alt
import pandas as pd
import sqlalchemy
import plotly.express as px

import time

# query = '''SELECT * FROM covid19_basic_differences '''

query = ''' SELECT
            	cbd.date,
                DATE_ADD(cbd.date, INTERVAL(-WEEKDAY(cbd.date)) DAY) week_monday,
            	cbd.country,
            	cbd.confirmed,
            	cbd.deaths,
            	cbd.recovered,
            	CASE WHEN cbd.country = 'US' THEN 'North America'
            		 WHEN cbd.country = 'Czechia' THEN 'Europe'
            		 ELSE continent END continent,
            	iso3
            FROM covid19_basic_differences cbd
            LEFT JOIN countries c
            	ON cbd.country = c.country
            LEFT JOIN country_codes cc
            	ON cbd.country = cc.country
            WHERE 1=1
            	AND confirmed >=0
            	AND deaths >= 0
            	AND recovered >= 0
        '''

st.set_page_config(
    page_title="Covid dashboard",
    page_icon=":puke:",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache(allow_output_mutation=True)
def get_connection():
    user = "student"
    password = "p7%40vw7MCatmnKjy7"
    conn_string = f"mysql+pymysql://{user}:{password}@data.engeto.com/data"
    alchemy_conn = sqlalchemy.create_engine(conn_string)
    return alchemy_conn

@st.cache(allow_output_mutation=True)
def data_load(query):
    df = pd.read_sql(query, get_connection())
    return df


def create_linechart(df, filter_continent, filter_country, xaxis, measure, blockname=st):
    if filter_country:
        chrt = alt.Chart(df).mark_line(point=True).encode(
            x=f'{xaxis}',
            y=f'sum_measure:Q',
            color='country',
            tooltip=alt.Tooltip([f'{xaxis}', 'sum_measure:Q', 'country'])
        ).transform_aggregate(
            sum_measure = f'sum({filter_measure})',
            groupby=[f'{xaxis}','country']
        ).interactive()

    elif filter_continent:
        chrt = alt.Chart(df).mark_line(point=True).encode(
            x=f'{xaxis}',
            y=f'sum_measure:Q',
            color='continent',
            tooltip=alt.Tooltip([f'{xaxis}', 'sum_measure:Q', 'continent'])
        ).transform_aggregate(
            sum_measure = f'sum({filter_measure})',
            groupby=[f'{xaxis}','continent']
        ).interactive()
    else:
        chrt = alt.Chart(df).mark_line(point=True).encode(
            x=f'{xaxis}',
            y=f'sum_measure:Q',
            tooltip=alt.Tooltip([f'{xaxis}', 'sum_measure:Q'])
        ).transform_aggregate(
            sum_measure = f'sum({filter_measure})',
            groupby=[f'{xaxis}']
        ).interactive()

    blockname.altair_chart(chrt, use_container_width=True)
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# start = time.time()

# base data
df = data_load(query)
df = df[~df['continent'].isna()]


##filters # -------------------------------------------------------------------------
st.sidebar.header('COVID DASHBOARD')
mode = st.sidebar.radio('Display:', ('Charts', 'Globe'))
if mode == 'Charts':
    st.sidebar.header('Filters')

    #date filter
    dates_options = list(df.date.unique())
    filter_date = st.sidebar.slider('Select date range:', min(dates_options), max(dates_options), (min(dates_options), max(dates_options)))

    #continent and country filter
    continent_options = list(df.continent.unique())
    filter_continent = st.sidebar.multiselect('Select continent:', continent_options)

    if filter_continent:
        filtered_df = df[df['continent'].isin(filter_continent)]
        country_options = list(filtered_df.country.unique())
        filter_country = st.sidebar.multiselect('Select country', country_options)
        if filter_country:
            filtered_df = df[df['country'].isin(filter_country)]

    else:
        country_options = list(df.country.unique())
        filter_country = st.sidebar.multiselect('Select country', country_options)
        if filter_country:
            filtered_df = df[df['country'].isin(filter_country)]
        else:
            filtered_df = df
## main part --------------------------------------------------------------------------------
## linecharts
    st.header('Covid data visualization')
    filter_measure = st.selectbox('Select measure',('confirmed', 'deaths', 'recovered'))


    # filter data by date filters
    filtered_df = filtered_df[ (filtered_df['date'] >= filter_date[0]) & (filtered_df['date'] <= filter_date[1]) ]
    st.write('')
    st.subheader(f'Daily differences - {filter_measure}')
    create_linechart(filtered_df, filter_continent, filter_country, 'date', filter_measure)

    st.write('')
    c1, c2 = st.beta_columns((1,1))
    c1.subheader(f'Weekly differences - {filter_measure}')
    create_linechart(filtered_df, filter_continent, filter_country, 'week_monday', filter_measure, blockname=c1)

## barchart dow
    filtered_df['dow'] = pd.to_datetime(filtered_df['date']).dt.day_name()

    chrt2 = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X('dow', sort = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']),
        y=f'mean({filter_measure})',
        tooltip = alt.Tooltip(['dow', f'mean({filter_measure})']),
        color='dow'
    ).interactive()


    c2.subheader(f'Averages over weekdays - {filter_measure}')
    c2.altair_chart(chrt2, use_container_width=True)

    # end = time.time()
    # st.write('Time:')
    # st.write(end - start)
# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------
if mode == 'Globe':
    df = df[(~df['continent'].isna())]
    df = df[(~df['iso3'].isna())]

    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.strftime('%Y-%m')
    df = df.groupby(['month_year', 'country', 'iso3', 'continent']).sum()[['confirmed', 'recovered', 'deaths']].reset_index()

    fig = px.scatter_geo(df,
                         locations='iso3',
                         color='continent',
                         hover_name='country',
                         size='confirmed',
                         projection='orthographic',
                         animation_frame = 'month_year',
                         width=800, height=800
                        )


    st.header('Confirmed cases on the globe')
    st.plotly_chart(fig)

## grouped bar chart
    df21 = df[['month_year','confirmed']].rename(columns={'confirmed':'value'})
    df21['measure'] = 'confirmed'
    df22 = df[['month_year','recovered']].rename(columns={'recovered':'value'})
    df22['measure'] = 'recovered'
    df23 = df[['month_year', 'deaths']].rename(columns={'deaths':'value'})
    df23['measure'] = 'deaths'
    df2 = pd.concat([df21,df22,df23], axis=0)

    expander = st.beta_expander(label='Year-Month confirmed, recovered, deaths')
    with expander:

        pick = st.multiselect('Measure', ('confirmed', 'recovered', 'deaths'), default='confirmed')

        df2 = df2[df2['measure'].isin(pick)]
        fig2 = alt.Chart(df2).mark_bar(size=15).encode(
            x=alt.X('measure', title=''),
            y='sum(value)',
            color='measure',
            column = 'month_year'
        ).properties(width={"step": 17})


        st.altair_chart(fig2)
