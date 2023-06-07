
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import datetime
import numpy as np
import streamlit_authenticator as stauth
import yaml
import datetime
import sqlite3
import mysql.connector
from streamlit_modal import Modal


st.set_page_config(layout="wide")

use_mysql = False
first_time_filter = True

# token = st.secrets["MAPBOX_TOKEN"]
token = "pk.eyJ1Ijoiam9obmRvZWVkc2Z1ZXIiLCJhIjoiY2xkbXVtd28yMDRrdDN1czR4MHJlMXZoMiJ9.zVn-NQ0bJKI052eCjX9mZw"

def insert_login_mysql(name, logintime):
    host, dbname, usr_name, pswd, port = st.secrets["DB_HOST"], st.secrets["DB_NAME"], st.secrets["DB_USER"], st.secrets["DB_PSWD"], st.secrets["DB_PORT"]
    mydb  = mysql.connector.connect(
        host=host,
        database=dbname,
        user=usr_name,
        password=pswd,
        port=port
    )
    mycursor = mydb.cursor()

    sql = ''' INSERT INTO login(name,logintime)
              VALUES(%s,%s) '''
    mycursor.execute(sql, (name, logintime))
    mydb.commit()
    mydb.close()
    


def insert_login(name, logintime):
    conn = sqlite3.connect('tracker.db')
    sql = ''' INSERT INTO login(name,logintime)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (name, logintime))
    conn.commit()
    conn.close()


# @st.cache(ttl=24*60*60)
def get_distance(point1: dict, point2: dict) -> tuple:
    """Gets distance between two points en route using http://project-osrm.org/docs/v5.10.0/api/#nearest-service"""
    
    url = f"""http://router.project-osrm.org/route/v1/driving/{point1["lon"]},{point1["lat"]};{point2["lon"]},{point2["lat"]}?overview=false&alternatives=false"""
    r = requests.get(url)
    
    # get the distance from the returned values
    try:
        route = json.loads(r.content)["routes"][0]
        distance = route["distance"]
        distance_km = round(distance/1000, 2)
        duration = route["duration"]
        return (distance_km, duration.str(datetime.timedelta(seconds=duration)).split(".")[0])
    except:
        return ('Oops:( Could not Get the data right now', None)

num_cols = []
@st.cache(ttl=24*60*60)
def get_data():
    df = pd.read_excel('20220105-2015.xlsx')
    cols = ['Reporting Company Trade Name / Nom commercial de la société déclarante', 'Facility Name',
            "English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais"
            ]
    for col in cols:
        try:
            df[col] = df[col].str.lower()
        except:
            pass
    co2_column = 'Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)'
    df[co2_column] = pd.to_numeric(df[co2_column], errors='coerce')
    num_cols.extend(df._get_numeric_data().columns)

    return df


    
    # components.html('''
    # <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
    # <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    # <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js"></script>
    # <script>
    #     $(document).ready(function(){
    #         $("#myModal").modal('show');
    #     });
    # </script>
    # <div id="myModal" class="modal fade">
    #     <div class="modal-dialog">
    #         <div class="modal-content">
    #             <div class="modal-header">
    #                 <h5 class="modal-title">Message Box</h5>
    #                 <button type="button" class="close" data-dismiss="modal">&times;</button>
    #             </div>
    #             <div class="modal-body">
    #                 <p>This is a message Box</p>
                    
    #             </div>
    #         </div>
    #     </div>
    # </div>''', height=300)
        





    # modal = Modal("Message Box" , key=1)
    # if first_time_filter:
    #     modal.open()
    #     first_time_filter = False 


    # if modal.is_open():
    #     with modal.container():
    #         st.write("Text goes here")

    # modal.close()

df = get_data()
# agree = True
reporting_axis = 'Reporting Company Trade Name / Nom commercial de la société déclarante'
industry_axis = "English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais"
co2_column = 'Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)'

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
    (.1, 2.3, .1, 1.3, .1))
with row0_1:
    st.title('Analyzer')


################
### ANALYSIS ###
################

# @st.cache(ttl=24*60*60)
def chart1_data(band, year):
    df_filtered = df[df['Reference Year / Année de référence'] == year]
    df_filtered = df_filtered[df_filtered['Band Name'].isin(band)]
    df_filtered = df_filtered[df_filtered['Duration'] <= max_dist*3600]
    return df_filtered


def chart1(df_filtered):
    # st.balloons()
    if agree:
        df_tmp = df_filtered.groupby(reporting_axis, as_index=False)[co2_column].sum()
        df_tmp = df_tmp.sort_values(co2_column, ascending=False)
        top_15 = df_tmp[reporting_axis].head(15).unique()
        df_filtered = df_filtered.loc[df_filtered[reporting_axis].isin(top_15)]

    total_df_filtered  = df_filtered.groupby(['Facility Name', 'Reporting Company Trade Name / Nom commercial de la société déclarante'])[
        'Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)'].sum().sort_values(ascending=False).reset_index()
    

    if len(total_df_filtered["Reporting Company Trade Name / Nom commercial de la société déclarante"]) > 10:
        leg = -1.05
    elif len(total_df_filtered["Reporting Company Trade Name / Nom commercial de la société déclarante"]) > 5:
        leg = -0.5
    else:
        leg = -0.2

    fig = px.bar(total_df_filtered, x="Reporting Company Trade Name / Nom commercial de la société déclarante", y="Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)",
                color='Facility Name')
    fig.update_layout(template='simple_white', xaxis_title='Reporting Company', xaxis={'categoryorder': 'total ascending'},
                    legend=dict(orientation="h", yanchor="top",
                                y=leg, xanchor="right", x=1),
                    yaxis_title='Total Emissions (tonnes CO2e)', title='Total Emissions by Corporation', height=600)  # barmode='stack'
    st.plotly_chart(fig, use_container_width=True)


# @st.cache(ttl=24*60*60)
def chart2_data(band, year):
    df_filtered = df[df['Reference Year / Année de référence'] == year]
    df_filtered = df_filtered[df_filtered['Band Name'].isin(band)]
    return df_filtered


def chart2(df_filtered):
    
    if agree:
        # try:
        #     df_tmp = df_filtered.groupby(industry_axis, as_index=False).sum()
        # except:
        #     df_tmp = df_filtered2.groupby(industry_axis, as_index=False)[num_cols].sum()

        df_tmp = df_filtered2.groupby(industry_axis, as_index=False)[co2_column].sum()
        try:
            df_tmp = df_tmp.sort_values(co2_column, ascending=False)
        except:
            pass
        top_15 = df_tmp[industry_axis].head(15).unique()
        df_filtered = df_filtered.loc[df_filtered[industry_axis].isin(top_15)]
    
    total_df_filtered = df_filtered.groupby(['Facility Name', industry_axis])[
        'Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)'].sum().sort_values(ascending=False).reset_index()
    
    
    fig = px.bar(total_df_filtered, x="English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais", y="Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)",
                color='Facility Name')

    if len(total_df_filtered["English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais"]) > 10:
        leg = -1.05
    else:
        leg = -0.2

    fig.update_layout(template='simple_white', xaxis_title='Industry Type', xaxis={'categoryorder': 'total ascending'},
                    legend=dict(orientation="h", yanchor="top",
                                y=leg, xanchor="right", x=1),
                    yaxis_title='Total Emissions (tonnes CO2e)', title='Total Emissions by Industry Type', height=600)  # barmode='stack'
    st.plotly_chart(fig, use_container_width=True)


# @st.cache(ttl=24*60*60)
def chart3_data(band):
    df2 = df[df['Band Name'].isin(band)]
    color = "English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais"
    top_cats = df2[color].value_counts().head(10).index.tolist()
    df2.loc[~df2[color].isin(top_cats), color] = 'Others'
    return df2


def chart3(df2):
    fig = px.bar(df2, y='Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)', x='Reference Year / Année de référence',
                color="English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais")

    # fig.update_layout(template='simple_white',
    #                   title=' Total Emissions per Refrence Year', height=600)
    fig.update_layout(template='simple_white', yaxis_title='Total Emissions (tonnes CO2e)',
                    title='Changes in Emissions Over Time', height=600,
                    legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="right", x=1, title='NAICS Code'))

    st.plotly_chart(fig, use_container_width=True)


def chart4(data):
    fig = go.Figure()

    report_col = 'Reporting Company Trade Name / Nom commercial de la société déclarante'

    data[report_col] = data[report_col].fillna('None') 

    data_star = data[data['Location Data Type'].str.lower() == 'band']
    data_not_star = data[data['Location Data Type'].str.lower() == 'facility']

    for fac in data_star[report_col].unique():
        data_fac = data_star[data_star[report_col] == fac]
        fig.add_trace(go.Scattermapbox(
            lon=data_fac['Longitude'],
            lat=data_fac['Latitude'],
            text=data_fac['Facility Name'], name=fac,
            mode='markers', marker=dict(
                symbol='star', size=20

            )))

    for fac in data_not_star[report_col].unique():
        data_fac = data_not_star[data_not_star[report_col] == fac]
        fig.add_trace(go.Scattermapbox(
            lon=data_fac['Longitude'],
            lat=data_fac['Latitude'],
            text=data_fac['Facility Name'], name=fac, 
            mode='markers'))

    fig.update_layout(
        mapbox_style="outdoors",
        geo_scope='north america', height=700,
        # legend=dict(orientation="h", yanchor="top", y=-0.02,
        #             xanchor="right", x=0.5, title='Location Data Type')
    )

    try:
        lon_foc, lat_foc = data_not_star.iloc[0]['Longitude'], data_not_star.iloc[0]['Latitude']
    except:
        lon_foc, lat_foc = data_star.iloc[0]['Longitude'], data_star.iloc[0]['Latitude']

    fig.update_layout(
        mapbox=dict(
            accesstoken=token,
            zoom=2,  # this is kind of like zoom
            # this will center on the point
            center=dict(lat=lat_foc, lon=lon_foc),
        ))
    st.plotly_chart(fig, use_container_width=True)


    # combination = itertools.combinations(list(data['Facility Name']),2)
    # dist_array = []
    # for i , r in data.iterrows():
    #     point1 = {"lat": r["Latitude"], "lon": r["Longitude"]}
    #     for j, o in data[data.index != i].iterrows():
    #         point2 = {"lat": o["Latitude"], "lon": o["Longitude"]}
    #         dist, duration = get_distance(point1, point2)
    #         #dist = geodesic((i_lat, i_lon), (o["CapitalLatitude"], o["CapitalLongitude"])).km
    #         dist_array.append((i, j, duration, dist))
    # distances_df = pd.DataFrame(dist_array,columns=["origin","destination","duration(s)","distnace(m)"])
    # distances_df = distances_df.merge(data[["Facility Name"]], left_on = "origin", right_index=True).rename(columns={"Facility Name":"origin_name"})
    # distances_df = distances_df.merge(data[["Facility Name"]], left_on = "destination", right_index=True).rename(columns={"Facility Name":"destination_name"})
    # distances_df['duration(s)'] = distances_df['duration(s)'].apply(lambda x: str(datetime.timedelta(seconds=x)))
    # st.dataframe(data=distances_df.astype(str).reset_index(drop=True))

def chart5(data):
    em_col = 'Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)'
    fig = px.scatter(data.dropna(subset=[em_col]), x="Distance", y="Duration", size=em_col,
                color='Reporting Company Trade Name / Nom commercial de la société déclarante', hover_data=['Facility Name', em_col],
                labels={'Distance': 'Distance (meters)', 'Duration': 'Duration (seconds)'},
                title='Distance v/s Duration')
    fig.update_layout(template='simple_white', height=600, legend_title_text='Reporting Company', legend=dict(orientation="h", yanchor="top",
                                y=-0.7, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)


styl = """
<style>
.plot-container{
box-shadow: 4px 4px 8px 4px rgba(0,0,0,0.2);
transition: 0.3s;

}
</styl>
"""
st.markdown(styl, unsafe_allow_html=True)



with st.sidebar:
    st.subheader('Configure the Plots')
    band_chart = st.multiselect("Please select Primary Band Name", list(
            df['Band Name'].unique()), key='band_chart', default=["Tsuut'ina Nation"])
    
    
    data_dist = df[df['Band Name'].isin(band_chart)]
    min_d = float(data_dist['Duration'].min()) / 3600
    max_d = float(data_dist['Duration'].max()) / 3600

    max_dist = st.slider(
        'Select a range for Driving Duration (in hours)', min_value=min_d, max_value=max_d, value=max_d, step=0.5)
    agree = st.checkbox('Limit to top 15 bars', value=True)
    
    

    




row4_spacer1, row4_1, row4_spacer2 = st.columns((.2, 7.1, .2))
with row4_1:
    st.subheader('Total Emissions by Corporation')
row5_spacer1, row5_1, row5_spacer2, row5_2, row5_spacer3 = st.columns(
    (.2, 2.3, .4, 4.4, .2))
with row5_1:
    year_chart1 = st.selectbox("Please Select year", list(
        df['Reference Year / Année de référence'].unique()), key='year_chart1', index=4)
    st.markdown('This chart shows what corporations are emitting and in what volumes within 100km of the selected band in the selected year.')
    st.markdown(
        'The size of bar indicates the total emissions released over the selected year by each corporation.')
    st.markdown(
        'The color of the bar is associated with the name of the emitting facility.')
    st.markdown('Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome.')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')

with row5_2:
    df_filtered = chart1_data(band_chart, year_chart1)
    chart1(df_filtered)
    see_data = st.expander('You can click here to see the data 👉')
    with see_data:
        st.dataframe(data=df_filtered.astype(str).reset_index(drop=True))


row6_spacer1, row6_1, row6_spacer2 = st.columns((.2, 7.1, .2))
with row6_1:
    st.subheader('Total Emissions by Industry Type')
row7_spacer1, row7_1, row7_spacer2, row7_2, row7_spacer3 = st.columns(
    (.2, 2.3, .4, 4.4, .2))
with row7_1:
    year_chart2 = st.selectbox("Please select year", list(
        df['Reference Year / Année de référence'].unique()), key='year_chart2', index=4)
    st.markdown('''This chart describes what types of industries are operating within 100 kilometers of the selected band name. 

The size of bar indicates the total emissions released over the selected year. 

The color of the bar is associated with the name of the emitting facility. 

Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome. 
''')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')
with row7_2:
    df_filtered2 = chart2_data(band_chart, year_chart2)
    chart2(df_filtered2)
    see_data2 = st.expander('You can click here to see the data 👉')
    with see_data2:
        st.dataframe(data=df_filtered2.astype(str).reset_index(drop=True))


row8_spacer1, row8_1, row8_spacer2 = st.columns((.2, 7.1, .2))
with row8_1:
    st.subheader('Changes in Emissions Over Time')
row9_spacer1, row9_1, row9_spacer2, row9_2, row9_spacer3 = st.columns(
    (.2, 2.3, .4, 4.4, .2))
with row9_1:
    st.markdown('''This chart describes changes in emissions over time within 100 km of the selected First Nation. 

The size of bar indicates the total emissions released over the selected year. 

The color of the bar is associated with the type of industry. 

Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome. ''')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')
with row9_2:
    df2 = chart3_data(band_chart)
    chart3(df2)
    see_data3 = st.expander('You can click here to see the data 👉')
    with see_data3:
        st.dataframe(data=df2.astype(str).reset_index(drop=True))


row10_spacer1, row10_1, row10_spacer2 = st.columns((.2, 7.1, .2))
with row10_1:
    st.subheader('Map of Emitting Facilities and Bands')
row11_spacer1, row11_1, row11_spacer2, row11_2, row11_spacer3 = st.columns(
    (.2, 2.3, .4, 4.4, .2))
with row11_1:
    year_chart4 = st.selectbox("Please elect year", list(
        df['Reference Year / Année de référence'].unique()), key='year_chart4', index=4)
    df_filtered4 = chart1_data(band_chart, year_chart4)


    st.markdown('''This map describes emitting facilities within 100km of the selected band. Adjacent bands within a 100km radius are also displayed. All bands are displayed as stars. 

The circles on the map describe facility locations. The circles are colored by the polluting/emitting corporation. 

Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome.''')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')
with row11_2:
    
    chart4(df_filtered4)
    see_data4 = st.expander('You can click here to see the data 👉')
    with see_data4:
        st.dataframe(data=df_filtered4.astype(str).reset_index(drop=True))


# _, row66_1, _ = st.columns((.2, 7.1, .2))
# with row66_1:
#     st.subheader('Distance v/s Duration Plot')
# _, row77_1, _, row77_2, _ = st.columns(
#     (.2, 2.3, .4, 4.4, .2))
# with row77_1:
#     pass
# with row77_2:
#     df5 = chart3_data(band_chart)
#     chart5(df5)



# see_data5 = st.expander('You can click here to see the tracker 👉')

# def login_data():
#     cnx = sqlite3.connect('tracker.db')
#     login_df = pd.read_sql_query("SELECT * FROM login", cnx).drop_duplicates()
#     cnx.close()
#     d = login_df.groupby('name').agg({'logintime': ['count', 'last']}).reset_index()
#     d.columns = ['Name', 'Count', "Last"]
#     return d


# def login_data_mysql():
#     host, dbname, usr_name, pswd, port = st.secrets["DB_HOST"], st.secrets["DB_NAME"], st.secrets["DB_USER"], st.secrets["DB_PSWD"], st.secrets["DB_PORT"]
#     mydb  = mysql.connector.connect(
#         host=host,
#         database=dbname,
#         user=usr_name,
#         password=pswd,
#         port=port
#     )
#     login_df = pd.read_sql('SELECT * FROM login', con=mydb)
#     mydb.close()
#     d = login_df.groupby('name').agg({'logintime': ['count', 'last']}).reset_index()
#     d.columns = ['Name', 'Count', "Last"]
#     return d

# with see_data5:
#     if use_mysql:
#         login_df = login_data_mysql()
#     else:
#         login_df = login_data()
#     st.dataframe(data=login_df.astype(str).reset_index(drop=True))