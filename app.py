import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as make_subplots

st.set_page_config(layout="wide")

# https://plotly.github.io/plotly.py-docs/generated/plotly.express.scatter_mapbox.html
# https://plotly.com/python/scattermapbox/
@st.cache(allow_output_mutation=True)
def data():
    df_train = pd.read_csv("./dataset/train.csv")
    df_spray = pd.read_csv("./dataset/spray.csv")
    df_weather = pd.read_csv("./dataset/weather.csv")
    df_test = pd.read_csv("./dataset/test.csv")
    return [df_train, df_spray, df_weather, df_test]


df = data()
df_train = df[0]
df_spray = df[1]
df_weather = df[2]
df_test = df[3]
# trap_locations = df_train[["Longitude", "Latitude", "Trap", "Date"]].drop_duplicates()

# Change date column to be datetime dtype
def date_add(df):
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()
    df["Year"] = df.index.year
    df["Month"] = df.index.month
    df["Day"] = df.index.day
    return df


df_train = date_add(df_train)
df_spray = date_add(df_spray)
df_weather = date_add(df_weather)

px.set_mapbox_access_token(open('./.gitignore/.mapbox_token.txt').read())

# # map
# st.sidebar.title("🦟 Identifying presence of West Nile Virus per Trap")
# st.sidebar.info("## All Traps 🪤 map")
# # st.map(locations) # plots all points at once
# px.set_mapbox_access_token(open("../.gitignore/.mapbox_token.txt").read())

tab1, tab2 = st.tabs(["Overall", "Spray"])

# My part
# Arrangement of dataframe
# Create a copy of the dataframe to work with
df1 = df_train.copy()
# df1["Year"] = df1.index.year
# df1["Month"] = df1.index.month
# df1["Day"] = df1.index.day
# df1.index = pd.to_datetime(df1.index)

overall_date = (
    df1.groupby([pd.Grouper(freq="Y"), "Address"])
    .agg(
        {
            "NumMosquitos": "sum",
            "WnvPresent": "sum",
            "Latitude": "median",
            "Longitude": "median",
        }
    )
    .reset_index()
)

overall_date["Date"] = overall_date["Date"].dt.date

total_mos_wnv_years = px.scatter_mapbox(
    overall_date,
    lat="Latitude",
    lon="Longitude",
    color="WnvPresent",
    size="NumMosquitos",
    color_continuous_scale=px.colors.sequential.Viridis,
    hover_data=["NumMosquitos", "WnvPresent"],
    animation_frame="Date",
    zoom=9,
    width=1000,
    height=900,
)

total_mos_wnv_years.update_layout(
    title="Total Mosquitoes and Wnv over the years",
    # mapbox_style="",
)

# df_train_year = df1.groupby(["Year"], as_index=False).sum()

# mos_year_bar = px.bar(
#     df_train_year,
#     x="Year",
#     y="NumMosquitos",
#     # barmode="stack",
#     title="Total Mosquitoes over the years",
# )
# # year_bar.update_layout(hovermode="x unified")

# wnv_year_bar = px.bar(
#     df_train_year,
#     x="Year",
#     y="WnvPresent",
#     # barmode="stack",
#     title="Total Wnv Mosquito over the years",
# )

# trap_count = px.bar(
#     df1.resample("Y")["Trap"].count().reset_index(),
#     x="Date",
#     y="Trap",
#     title="Number of traps over the years",
# )

with tab1:
    st.header("Overall")
    # col1, col2 = st.columns(2)
    # col1.plotly_chart(mos_year_bar)
    # col2.plotly_chart(wnv_year_bar)
    # st.plotly_chart(trap_count)
    st.plotly_chart(total_mos_wnv_years)


# 2nd tab - To see the effectiveness of spraying
overall_add = (
    df1.groupby(["Address"])
    .agg(
        {
            "NumMosquitos": "sum",
            "WnvPresent": "sum",
            "Latitude": "median",
            "Longitude": "median",
        }
    )
    .reset_index()
)

df_spray_copy = df_spray.reset_index().copy()
df_spray_copy = date_add(df_spray_copy)
df_spray1 = df[1]
df_spray1["Date"] = pd.to_datetime(df_spray1["Date"])

spray_loc = px.scatter_mapbox(
    df_spray1,
    lat="Latitude",
    lon="Longitude",
    size_max=15,
    zoom=9,
    color_discrete_sequence=["palegreen"],
    opacity=0.5,
    animation_frame='Date',
    width=1000,
    height=900,
)

fig2 = px.scatter_mapbox(
    overall_add,
    lat="Latitude",
    lon="Longitude",
    size="NumMosquitos",
    color="WnvPresent",
    color_continuous_scale=px.colors.sequential.Viridis,
    zoom=9,
)
spray_loc.add_trace(fig2.data[0])
spray_loc.update_layout(title="Spray Locations", mapbox_style="open-street-map")

# Spraying for year 2011
overall_add = (
    df1.groupby(["Year", "Address"])
    .agg(
        {
            "NumMosquitos": "sum",
            "WnvPresent": "sum",
            "Latitude": "median",
            "Longitude": "median",
        }
    )
    .reset_index()
)

spray_loc_2011 = px.scatter_mapbox(
    df_spray_copy.query("Year == 2011"),
    lat="Latitude",
    lon="Longitude",
    size_max=15,
    zoom=9,
    color_discrete_sequence=["palegreen"],
    opacity=0.5,
    # animation_frame="Date",
    width=600,
    height=600,
)

fig2 = px.scatter_mapbox(
    overall_add.query("Year == 2011"),
    lat="Latitude",
    lon="Longitude",
    size="NumMosquitos",
    color="WnvPresent",
    color_continuous_scale=px.colors.sequential.Viridis,
    zoom=9,
)

spray_loc_2011.add_trace(fig2.data[0])

spray_loc_2011.update_layout(
    title="Spray Locations - 2011", mapbox_style="open-street-map"
)

#  Spraying for year 2013
spray_loc_2013 = px.scatter_mapbox(
    df_spray_copy.query("Year == 2013"),
    lat="Latitude",
    lon="Longitude",
    size_max=15,
    zoom=9,
    color_discrete_sequence=["palegreen"],
    opacity=0.5,
    # animation_frame="Date",
    width=600,
    height=600,
)

fig2 = px.scatter_mapbox(
    overall_add.query("Year == 2013"),
    lat="Latitude",
    lon="Longitude",
    size="NumMosquitos",
    color="WnvPresent",
    color_continuous_scale=px.colors.sequential.Viridis,
    zoom=9,
)

spray_loc_2013.add_trace(fig2.data[0])

spray_loc_2013.update_layout(
    title="Spray Locations - 2013", mapbox_style="open-street-map"
)

# Put chart up
with tab2:
    st.header("Spray")
    st.plotly_chart(spray_loc)
    col1, col2 = st.columns(2)
    col1.plotly_chart(spray_loc_2011)
    col2.plotly_chart(spray_loc_2013)
