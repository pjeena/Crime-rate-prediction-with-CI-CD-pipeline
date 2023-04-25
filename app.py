from flask import Flask,request,render_template
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from sklearn.preprocessing import StandardScaler
from src.pipeline.predict_pipeline import PredictPipeline
from src.utils import fetch_temperature_data

from datetime import datetime, timedelta
import requests
import numpy as np
import pandas as pd
import streamlit as st
import geopandas as gpd
import pydeck as pdk
from PIL import Image
import folium
from streamlit_folium import st_folium, folium_static
import branca


def popup_html(row):
    i = row
    district_name=df_folium['police_district'].iloc[i] 
    no_of_crimes=df_folium['no_of_crimes'].iloc[i]


    left_col_color = "#19a7bd"
    right_col_color = "#f2f0d3"
    
    html = """<!DOCTYPE html>
                <html>

                <head>
                <h4 style="margin-bottom:5"; width="10px">{}</h4>""".format(district_name) + """

                </head>
                    <table style="height: 30px; width: 30px;">
                <tbody>
                <tr>
                <td style="background-color: """+ left_col_color +""";"><span style="color: #ffffff;"># of Crimes</span></td>
                <td style="width: 40px;background-color: """+ right_col_color +""";">{}</td>""".format(no_of_crimes) + """
                </tr>

                </tbody>
                </table>
                </html>
                """
    return html





st.set_page_config(layout="wide")
#col1, col2, col3 = st.columns(3)
#col4, col5, col6 = st.columns(3)


# title
# current_date = datetime.strptime('2023-01-05 12:00:00', '%Y-%m-%d %H:%M:%S')
#current_date = pd.to_datetime(datetime.utcnow()).floor('H')
st.title(f'Crime rate demographics in San Francisco :cop:')

#st.header(f'{current_date} UTC')


#st.markdown('Streamlit is **_really_ cool**.')
st.markdown('_This app predicts the number of crimes in San Francisco on any given date. This technology can lead to need-based  \
            resource allocation, including sending officials other than law enforcement to certain kinds of calls.\
            The code is open source and available [here](https://github.com/pjeena/Crime-rate-prediction-in-San-Francisco) on GitHub_\
            ')


st.markdown("""
    <style>
    .stRadio [role=radiogroup]{
        align-items: center;
        justify-content: center;
    }
    </style>
""",unsafe_allow_html=True)


"## 🎯 Do you want to try it ?"
choice = st.radio("", options=[ "Yes", "No"], horizontal=True)


##st.markdown(":green[$\sqrt{x^2+y^2}=1$] is a Pythagorean identity. :pencil:")

if choice == 'Yes':
    st.markdown(':computer: Enter the :blue[date] in the sidebar :arrow_left:')


    with st.sidebar:
        st.markdown('## Today :calendar: :')
        todays_date = datetime.today()
        yesterdays_date = todays_date - timedelta(days = 2)
        st.markdown(  ' ## :red[{}] , :green[{}] '.format( todays_date.strftime("%d/%m/%Y"), todays_date.strftime("%H:%M:%S") )  )


    
#        date_of_interest = datetime(year,month,day)
        weather = fetch_temperature_data(yesterdays_date, todays_date , latitude=37.7775, longitude= -122.416389,altitude=None)


        col_t, col2_ws = st.columns(2)
        col_t.metric("Temperature",  '{}°C'.format(weather['tavg'][1])  , np.round(weather['tavg'][1] - weather['tavg'][0], 2) )
        col2_ws.metric("Wind",  '{}km/h'.format(weather['wspd'][1]) , np.round(weather['wspd'][1] - weather['wspd'][0], 2 ) )


        day = st.selectbox(
            "**Day (DD)**", options=   ('',) +  tuple(np.arange(1, 32))
        )

        month = st.selectbox(
            "**Month (MM)**", options=  ('',) + tuple(np.arange(1, 13))
        )

        year = st.selectbox(
            "**Year (YYYY)**", options=  ('',) + tuple(np.arange(2018, 2051))
        )


        gsw_schedule = st.radio(
                        "# **Do the Golden State Warriors have a game today?**",
                        ('Yes', 'No'))

        

#elif choice == "Not sure":
#    with st.sidebar:
#        st.write('thanks')

 #   st.write('Thanks for stopping by')   


else:
    with st.sidebar:
        st.markdown('## Today :calendar:')
        st.markdown(  ' ## :red[{}] , :green[{}] '.format( datetime.today().strftime("%d/%m/%Y"), datetime.today().strftime("%H:%M:%S") )  )

    col_11, col_22, col_33 = st.columns(3)
    with col_22:

        st.markdown('##### Not an issue, have a good day :slightly_smiling_face:')   









if choice == 'Yes' and day != '' and month != '' and year != '':
#st.write(year)
    
    date_of_interest = datetime(year,month,day)
    weather = fetch_temperature_data(date_of_interest, date_of_interest , latitude=37.7775, longitude= -122.416389,altitude=None)

    if weather.empty:
        col_1, col_2, col_3 = st.columns(3)
        with col_2:
            st.markdown('######  :sos: The weather forecast is only available for the next 5 days from the current date. \
                        So, its not possible to predict the outcome for a very far date.')

    else:
        temperature = weather['tavg'][0]
        wind_speed = weather['wspd'][0]

        day_of_week = date_of_interest.strftime("%A")


        if gsw_schedule == 'Yes':
            game_day = 1.0
        else:
            game_day = 0.0

        dict_details = { 'police_district' : ['Bayview', 'Central', 'Ingleside', 'Mission', 'Northern',
                                            'Out of SF', 'Park', 'Richmond', 'Southern', 'Taraval',
                                        'Tenderloin'],
            'incident_day_of_week' : day_of_week,
            'avg_temperature' : temperature,
            'wind_speed' : wind_speed,
            'game_day' : game_day,
            'day' : int(day),
            'month' : int(month),
            'year' : int(year)
        }


        df = pd.DataFrame(dict_details)


        predict_pipeline=PredictPipeline()
        #print("Mid Prediction")
        #results=predict_pipeline.predict(df)
        #print("after Prediction")


        df['no_of_crimes'] = np.rint(predict_pipeline.predict(df)).astype(int)

    #    st.dataframe(df)
    #    st.write(game_day)

        ### got the dataframe , now plot it on folium


        # --- load districts coordinates
        sfpd = gpd.read_file("artifacts/Current Police Districts.geojson")
        sfpd['district'] = sfpd['district'].str.capitalize()
        sfpd = sfpd.rename(columns={"district": "police_district"})
        sfpd = sfpd[['police_district' , 'shape_leng', 'shape_area' , 'geometry']]


        df_folium = pd.merge(df,sfpd, on='police_district')
        df_folium = df_folium[['police_district', 'no_of_crimes', 'shape_leng', 'shape_area', 'geometry']]
        df_folium = gpd.GeoDataFrame(df_folium)


        m = folium.Map(location=[37.7775, -122.416389], zoom_start=11, tiles='CartoDB positron')



        for i, r in df_folium.iterrows():
            # Without simplifying the representation of each borough,
            # the map might not be displayed
            sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
            geo_j = sim_geo.to_json()
            geo_j = folium.GeoJson(data=geo_j,
                                style_function=lambda x: {'fillColor': 'orange'})
            folium.Popup(r['police_district']).add_to(geo_j)
            #folium.Popup(r['no_of_crimes']).add_to(geo_j)

            geo_j.add_to(m)


        #df_folium = df_folium.to_crs()
        df_folium['centroid'] = df_folium.centroid




        for i, r in df_folium.iterrows():
            lat = r['centroid'].y
            lon = r['centroid'].x
            html = popup_html(i)
            iframe = branca.element.IFrame(html=html,width=510,height=280)
            popup = folium.Popup(folium.Html(html, script=True), max_width=400,)

            folium.Marker(location=[lat, lon],
                        popup=popup).add_to(m)




    #st_data = folium_static(m, width=500)
    #st_data = folium_static(m, width=500)
    #st.dataframe(df_new)
    #st.dataframe(results)
    #st.write(df_new.info())
        col1, col2, col3 = st.columns(3)
        with col1:
        #    st.write('<p style="font-size:26px; color:red;">Temperature</p>',unsafe_allow_html=True)

            st.markdown(
                """
            <style>
            [data-testid="stMetricValue"] {
                font-size: 40px;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )


            st.markdown('### :red[**Entered date**] :date:')
            st.metric(label=" ", value=date_of_interest.strftime('%d-%m-%Y'))

            st.markdown('### :green[**Temperature**] :sun_behind_rain_cloud:')
            st.metric(label=" ", value='{} °C'.format(temperature))

            st.markdown('### :blue[**Wind Speed**] :tornado_cloud:')
            st.metric(label=" ", value=  '{} km/h'.format(wind_speed) )




        with col2:
            st_data = folium_static(m, width=500)



        with st.sidebar:
            st.markdown("#### :red[1.] To navigate the map, just click on the markers.")
            st.markdown("#### :red[2.] Each marker pops up and shows the name of district and the number of crimes forcasted by the model")
            st.markdown("#### :red[2.] District name can also be seen by clicking anywhere on a multipolygon on the map")

