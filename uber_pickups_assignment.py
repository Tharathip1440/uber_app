import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import datetime 
import plotly.figure_factory as ff

st.set_page_config(page_title="Uber NYC App", layout="wide")

st.title("Uber Pickups NYC - Assignment")

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data


#Load data
data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text('Done!')

#data

#Date input
st.sidebar.header("📅 Filter by date range")
available_dates = sorted(data[DATE_COLUMN].dt.date.unique())
min_date = min(available_dates)
max_date = max(available_dates)
selected_date_range = st.sidebar.date_input("Choose a date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    data_filtered = data[(data[DATE_COLUMN].dt.date >= start_date) & (data[DATE_COLUMN].dt.date <= end_date)]
    if data_filtered.empty:
        st.warning("No data available for the selected date range.")
        st.stop()
else:
    st.warning("Please select a valid date range.")
    st.stop() 

#Selectbox
# ⏰ Filter by predefined hour ranges using selectbox
st.sidebar.header("⏰ Select Hour Range")
hour_ranges = {
    "00:00 - 05:59": (0, 5),
    "06:00 - 11:59": (6, 11),
    "12:00 - 17:59": (12, 17),
    "18:00 - 23:59": (18, 23),
    "All Day (00:00 - 23:59)": (0, 23)
}
hour_selected = st.sidebar.selectbox("Choose hour range", list(hour_ranges.keys()))
start_hour, end_hour = hour_ranges[hour_selected]
data_filtered = data[data[DATE_COLUMN].dt.hour.between(start_hour, end_hour)]
st.write(f"Showing data from {start_hour:02d}:00 to {end_hour:02d}:59")

data_filtered

#Plotly chart - histogram
st.subheader(f"📊 Number of pickups by minute at {hour_selected}")
hist_data = data_filtered[DATE_COLUMN].dt.minute.value_counts().sort_index()
fig = px.bar(x=hist_data.index, y=hist_data.values, labels={'x': 'Minute', 'y': 'Number of pickups'},
             title='Pickups per minute')
st.plotly_chart(fig, use_container_width=True)

#Convert to 3D map using PyDeck
st.subheader("🗺️ 3D Map of pickups")
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=40.7128,
        longitude=-74.0060,
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=data_filtered,
            get_position='[lon, lat]',
            radius=100,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        ),
    ],
))


# Click button to count visits
if 'counter' not in st.session_state:
    st.session_state.counter = 0

if st.button("🔁 Click me!"):
    st.session_state.counter += 1

st.success(f"This page has run {st.session_state.counter} times.")
