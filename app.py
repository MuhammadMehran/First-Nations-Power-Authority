
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")


@st.cache
def get_data():
    df = pd.read_excel('database.xlsx')
    cols = ['Reporting Company Trade Name / Nom commercial de la société déclarante', 'Facility Name',
        "English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais"
       ]
    for col in cols:
        df[col] = df[col].str.lower()
    return df


df = get_data()

row0_spacer1, row0_1, row0_spacer2, row0_2, row0_spacer3 = st.columns(
    (.1, 2.3, .1, 1.3, .1))
with row0_1:
    st.title('Analyzer')


################
### ANALYSIS ###
################

@st.cache(ttl=24*60*60)
def chart1_data(band, year):
    df_filtered = df[df['Reference Year / Année de référence'] == year]
    df_filtered = df_filtered[df_filtered['Band Name'] == band]
    return df_filtered


def chart1(df_filtered):
    total_df_filtered = df_filtered.groupby(['Facility Name', 'Reporting Company Trade Name / Nom commercial de la société déclarante'])[
        'Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)'].sum().reset_index()

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


@st.cache(ttl=24*60*60)
def chart2_data(band, year):
    df_filtered = df[df['Reference Year / Année de référence'] == year]
    df_filtered = df_filtered[df_filtered['Band Name'] == band]
    return df_filtered


def chart2(df_filtered):
    total_df_filtered = df_filtered.groupby(['Facility Name', "English Facility NAICS Code Description / Description du code SCIAN de l'installation en anglais"])[
        'Total Emissions (tonnes CO2e) / Émissions totales (tonnes éq. CO2)'].sum().reset_index()

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


@st.cache(ttl=24*60*60)
def chart3_data(band):
    df2 = df[df['Band Name'] == band]
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

    data_star = data[data['Location Data Type'].str.lower() == 'band']
    data_not_star = data[data['Location Data Type'].str.lower() == 'facility']

    for fac in data_star['Facility Name'].unique():
        data_fac = data_star[data_star['Facility Name'] == fac]
        fig.add_trace(go.Scattergeo(
            lon=data_fac['Longitude'],
            lat=data_fac['Latitude'],
            text=data_fac['Facility Name'], name=fac,
            mode='markers', marker=dict(
                symbol='star'

            )))

    for fac in data_not_star['Facility Name'].unique():
        data_fac = data_not_star[data_not_star['Facility Name'] == fac]
        fig.add_trace(go.Scattergeo(
            lon=data_fac['Longitude'],
            lat=data_fac['Latitude'],
            text=data_fac['Facility Name'], name=fac,
            mode='markers'))

    fig.update_layout(
        mapbox_style="dark",
        geo_scope='north america', height=600,
        legend=dict(orientation="h", yanchor="top", y=-0.02,
                    xanchor="right", x=0.5, title='Location Data Type')
    )

    lon_foc, lat_foc = data_not_star.iloc[0]['Longitude'], data_not_star.iloc[0]['Latitude']

    fig.update_layout(
        geo=dict(
            projection_scale=3,  # this is kind of like zoom
            # this will center on the point
            center=dict(lat=lat_foc, lon=lon_foc),
        ))
    st.plotly_chart(fig, use_container_width=True)


row4_spacer1, row4_1, row4_spacer2 = st.columns((.2, 7.1, .2))
with row4_1:
    st.subheader('Total Emissions by Corporation')
row5_spacer1, row5_1, row5_spacer2, row5_2, row5_spacer3 = st.columns(
    (.2, 2.3, .4, 4.4, .2))
with row5_1:
    band_chart1 = st.selectbox("Please select Band Name", list(
        df['Band Name'].unique()), key='band_chart1', index=0)
    year_chart1 = st.selectbox("Please elect year", list(
        df['Reference Year / Année de référence'].unique()), key='year_chart1')
    st.markdown('This chart shows what corporations are emitting and in what volumes within 100km of the selected band in the selected year.')
    st.markdown(
        'The size of bar indicates the total emissions released over the selected year by each corporation.')
    st.markdown(
        'The color of the bar is associated with the name of the emitting facility.')
    st.markdown('Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome.')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')

with row5_2:
    df_filtered = chart1_data(band_chart1, year_chart1)
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
    band_chart2 = st.selectbox("Please select Band Name", list(
        df['Band Name'].unique()), key='band_chart2', index=363)
    year_chart2 = st.selectbox("Please select year", list(
        df['Reference Year / Année de référence'].unique()), key='year_chart2')
    st.markdown('''This chart describes what types of industries are operating within 100 kilometers of the selected band name. 

The size of bar indicates the total emissions released over the selected year. 

The color of the bar is associated with the name of the emitting facility. 

Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome. 
''')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')
with row7_2:
    df_filtered2 = chart2_data(band_chart2, year_chart2)
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
    band_chart3 = st.selectbox("Please select Band Name", list(
        df['Band Name'].unique()), key='band_chart3')
    st.markdown('''This chart describes changes in emissions over time within 100 km of the selected First Nation. 

The size of bar indicates the total emissions released over the selected year. 

The color of the bar is associated with the type of industry. 

Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome. ''')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')
with row9_2:
    df2 = chart3_data(band_chart3)
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
    band_chart4 = st.selectbox("Please select Band Name", list(
        df['Band Name'].unique()), key='band_chart4', index=363)
    year_chart4 = st.selectbox("Please elect year", list(
        df['Reference Year / Année de référence'].unique()), key='year_chart4')
    st.markdown('''This map describes emitting facilities within 100km of the selected band. Adjacent bands within a 100km radius are also displayed. All bands are displayed as stars. 

The circles on the map describe facility locations. The circles are colored by the polluting/emitting corporation. 

Data Challenges: Corporation names change, facilities and do not always meet reporting obligations. Feedback on the data is welcome.''')
    st.markdown(
        'Contact Alexandria Shrake at First Nations Power Authority for more detail. Email: Ashrake@fnpa.ca')
with row11_2:
    df_filtered4 = chart1_data(band_chart4, year_chart4)
    chart4(df_filtered4)
    see_data4 = st.expander('You can click here to see the data 👉')
    with see_data4:
        st.dataframe(data=df_filtered4.astype(str).reset_index(drop=True))
