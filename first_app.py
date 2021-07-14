import streamlit as st
import altair as alt
import pandas as pd
import sqlalchemy

import time

user = "student"
password = "p7%40vw7MCatmnKjy7"
conn_string = f"mysql+pymysql://{user}:{password}@data.engeto.com/data"
alchemy_conn = sqlalchemy.create_engine(conn_string)

query = '''SELECT * FROM covid19_basic_differences
                    WHERE 1=1
                    	AND date > '2020-11-01'
                    	AND date < '2021-06-01'
                        AND country = 'Czechia'
                 '''

def data_load(query, conn):
    df = pd.read_sql(query,
                conn,
                parse_dates=True
                )
    return df

# st.dataframe(df)

df = data_load(query, alchemy_conn)

# st.write(list(df['date'].unique())
datesmin = min(list(df['date'].unique()))
datesmax = max(list(df['date'].unique()))


values = st.sidebar.slider('slider', min_value = datesmin, max_value = datesmax, value=(datesmin, datesmax))

df = df[(df['date'] > values[0]) & (df['date'] < values[1])]



if st.sidebar.checkbox('Show dataframe'):

    option = st.sidebar.selectbox('aa', ['confirmed', 'deaths', 'recovered'])
    show = True
else:
    option = 'confirmed'
    show = False


if show == True:
    st.sidebar.write(df[['date',option]].set_index('date'))


chart = alt.Chart(df).mark_line().encode(
    x='date',
    y=option,
    color='country'
)



st.altair_chart(chart, use_container_width=True)


'Starting a long computation...'

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress(i + 1)
  time.sleep(0.0001)

'...and now we\'re done!'
