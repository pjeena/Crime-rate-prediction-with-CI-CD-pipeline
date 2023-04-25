import sys
import numpy as np
import pandas as pd
from datetime import datetime
import pymongo
from pymongo.write_concern import WriteConcern
import certifi

import warnings
warnings.filterwarnings("ignore")


from src.exception import CustomException
from src.logger import logging
#from src.utils import insert_data_to_mongodb


# Mongo DB insert and read funcitons
def insert_data_to_mongodb(df,database_name,table_name):

    try:
        client = pymongo.MongoClient('mongodb+srv://pjeena:chutiyapa@cluster0.u0qdxzq.mongodb.net/test')
        data = df.to_dict(orient='records')
        db = client[database_name]
        db[table_name].with_options(write_concern=WriteConcern(w=0)).insert_many(data,ordered=False)
        db[table_name].create_index( [ ('police_district' , 1), ('day' , 1,) , ('month' , 1), ('year' , 1) ]   , unique=True )
    except pymongo.errors.BulkWriteError as e:
        logging.error(e)







# we are only interested in data b/w these two dates
start_date = datetime(2018, 1, 1)
end_date = datetime.today()
end_date = end_date.replace(minute=0, hour=0, second=0, microsecond=0)



# reading police reports data and selecting relevant fields
df_incidents = pd.read_parquet('data/Police_Department_Incident_Reports_2018_1_1_to_today.parquet')
#columns_to_select = ['incident_date', 'incident_year', 'incident_day_of_week', 'incident_category',
#                     'incident_description', 'resolution', 'police_district', 'latitude', 'longitude']
#df_incidents = df_incidents[columns_to_select]
df_incidents['incident_date'] = pd.to_datetime(df_incidents['incident_date'])


# reading temperature data and selecting relevant fields
df_temperature = pd.read_parquet('data/Temperature_records_2018_1_1_to_today.parquet')
columns_to_select = ['time', 'tavg', 'wspd']
df_temperature = df_temperature[columns_to_select]
df_temperature['time'] = pd.to_datetime(df_temperature['time'])
df_temperature.rename(columns={"time": "incident_date", "tavg": "avg_temperature", "wspd" : "wind_speed"},inplace=True)


# reading GSW game schedule data and selecting relevant fields
df_gsw_schedule = pd.read_parquet('data/GSW_games_schedule_2018_1_1_to_today.parquet')
df_gsw_schedule.rename(columns={"Date": "incident_date", "Home": "home_or_away", "Result" : "result"},inplace=True)
df_gsw_schedule['incident_date'] = pd.to_datetime(df_gsw_schedule['incident_date'])
df_gsw_schedule['game_day'] = 1  # adding a column which shows that its a game day for GSW



## Validating data b/w the two dates  start_date = datetime(2018, 1, 1) &&  end_date = datetime(2023, 4, 14)
df_incidents = df_incidents[df_incidents['incident_date'] >= start_date]
df_incidents = df_incidents[df_incidents['incident_date'] <= end_date]

df_temperature = df_temperature[df_temperature['incident_date'] >= start_date]
df_temperature = df_temperature[df_temperature['incident_date'] <= end_date]

df_gsw_schedule = df_gsw_schedule[df_gsw_schedule['incident_date'] >= start_date]
df_gsw_schedule = df_gsw_schedule[df_gsw_schedule['incident_date'] <= end_date]




## Merging the three dataframes to form a collective dataset


df_meta = pd.merge(df_incidents, df_temperature, on='incident_date', how='left')
df_meta = pd.merge(df_meta, df_gsw_schedule,  on='incident_date', how='left')


df_meta['home_or_away'].fillna(3, inplace=True)   # here 3 indicates that there is no game
df_meta['result'].fillna('No game', inplace=True)  # if no W/L -> No game
df_meta['game_day'].fillna(0, inplace=True)       #

# saving data for dashboarding 
df_meta.to_parquet('data/data_for_EDA.parquet')
#insert_data_to_mongodb(df_meta,database_name='PoliceIncidents',table_name='data_EDA')





##     Preparing data from ML model-------------

#grouping data with difference of 1 day and police district
df_meta.set_index('incident_date',inplace=True)
df_meta = df_meta.groupby([pd.Grouper(freq="1D"), "police_district"]).agg({"incident_day_of_week":"first",
                                                                            "police_district":"count", 
                                                                            "avg_temperature":"mean", 
                                                                            "wind_speed":"mean",
                                                                            "game_day":"first"})
df_meta.rename(columns={"police_district":"no_of_crimes"}, inplace=True)

## extracting day , month, year
df_meta["day"] = df_meta.index.get_level_values(0).day         
df_meta["month"] = df_meta.index.get_level_values(0).month
df_meta["year"] = df_meta.index.get_level_values(0).year

df_meta.insert(len(df_meta.columns)-1, 'no_of_crimes', df_meta.pop('no_of_crimes')) ## shifting no_of_crimes to the last column
df_meta = df_meta.reset_index()
df_meta = df_meta.drop('incident_date',axis=1)



## Uploading data to mongoDB::
insert_data_to_mongodb(df_meta,database_name='PoliceIncidents',table_name='data_model_training')
#df_meta.to_parquet('data/data_for_model_training.parquet')