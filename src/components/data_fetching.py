import sys
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


from src.exception import CustomException
from src.logger import logging

from sodapy import Socrata
from datetime import datetime
import matplotlib.pyplot as plt
from meteostat import Point, Daily


##   Police Department Incident Reports: 2018 to Present ( data.sfgov.org )
def fetch_data_incidents(limit : int):
    '''
    This function fetches data from the San Francisco Data API, 
    limit -> no of records fetched
    '''
    # get client
    client = Socrata("data.sfgov.org", None)

    #get data from the API
    results = client.get("wg3w-h783", limit=limit)

    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    columns_to_select = ['incident_date', 'incident_year', 'incident_day_of_week', 'incident_category',
                     'incident_description', 'resolution', 'police_district', 'latitude', 'longitude']
    results_df = results_df[columns_to_select]

    return results_df




##   Temeperature records 2018 to present
def fetch_temperature_data(start_date : datetime, end_date : datetime, latitude : float, longitude : float, altitude : None):
    '''
    Outputs the temperature and other details of san francisco between two dates
    '''

    #Create Point for San Francisco
    san_francisco = Point(latitude, longitude)

    #Get daily data from 2018 - 2023 
    data_temp = Daily(san_francisco, start_date, end_date)
    data_temp = data_temp.fetch()
    data_temp = data_temp.reset_index()

    return data_temp




## Golden State Warriors (San Francisco based team) schedule since 2018
def fetch_gsw_data():
    '''
    reads gsw games data from csv file
    '''
    try :
        df_games = pd.read_csv('data/GSW_schedule.csv')
        logging.info('Read the gsw schedule dataset as df_games')
        return df_games
    except Exception as e:
        raise CustomException(e,sys)
    
    

if __name__=='__main__':
    ## We are only concerned between the folowing dates 
    start_date = datetime(2018, 1, 1)
    end_date = datetime.today()
    end_date = end_date.replace(minute=0, hour=0, second=0, microsecond=0)

    df_incidents = fetch_data_incidents(limit=200000)
    df_temperature = fetch_temperature_data(start_date, end_date , latitude=37.7775, longitude= -122.416389,altitude=None)
    df_gsw_schedule = fetch_gsw_data()


    df_incidents.to_parquet('data/Police_Department_Incident_Reports_2018_1_1_to_today.parquet')
    df_temperature.to_parquet('data/Temperature_records_2018_1_1_to_today.parquet')
    df_gsw_schedule.to_parquet('data/GSW_games_schedule_2018_1_1_to_today.parquet')

    print(df_incidents.shape, df_temperature.shape, df_gsw_schedule.shape)

