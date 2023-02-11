import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
"https://github.com/chairielazizi/streamlit-collision/blob/master/Motor_Vehicle_Collisions_-_Crashes.csv?raw=true"
)


def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://github.com/llorenc-fer/NYC-Collisions/blob/main/ICFF-Landing-Page-Header-Background-NYC.png?raw=true");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )


add_bg_from_url()

st.title("Motor Vehicle Collisions in NYC")

st.markdown("This application is a Streamlit Dashboard that can be used"
" to analyze motor vehicle collisions in NYC")
st.write("by Llorenç Fernández")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data.rename(columns={'crash_date_crash_time':'date/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data

# find the indices of the rows that contain latitudes outside the range of 35 to 50
latitude_indices_to_drop = data[(data['latitude'] < 35) | (data['latitude'] > 50)].index

# find the indices of the rows that contain longitudes outside the range of -70 to -75
longitude_indices_to_drop = data[(data['longitude'] < -75) | (data['longitude'] > -70)].index

# combine the indices of the rows to drop
indices_to_drop = latitude_indices_to_drop.union(longitude_indices_to_drop)

# drop the rows that contain latitudes or longitudes outside the specified ranges
data = data.drop(indices_to_drop)

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured in vehicle collissions", min_value=0, max_value=19, value=0)
st.map(data.query("injured_persons >= @injured_people")[['latitude', 'longitude']].dropna(how="any"))


st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour", 0,23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour+1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 10,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data = data[['date/time', "latitude", "longitude"]],
        get_position=['longitude', 'latitude'],
        radius=100, #radius of individual points
        extruded=True, #makes it 3d
        pickable=True,
        elevation_scale=4,
        elevation_range=[0,1000],
        ),
    ],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour+1) %24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour +1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("How many collisions occur during a given month?")
month = st.slider("Month", 1,12)
data = data[data['date/time'].dt.month == month]
st.subheader("Breakdown by month between %i and %i" % (month, (month+1) %12))
filtered = data[
    (data['date/time'].dt.month >= month) & (data['date/time'].dt.month < (month +1))
]
hist = np.histogram(filtered['date/time'].dt.month, bins=12, range=(0,12))[0]
chart_data = pd.DataFrame({'month': range(12), 'crashes':hist})
fig = px.bar(chart_data, x='month', y='crashes', hover_data=['month', 'crashes'], height=400)
st.write(fig)






st.header("Top 5 Dangerous Streets by affected type")
select = st.selectbox("Affected type of people", ['Pedestrians', 'Cyclists', "Motorists"])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[['on_street_name', "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[:5])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[['on_street_name', "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[['on_street_name', "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[:5])







if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)
