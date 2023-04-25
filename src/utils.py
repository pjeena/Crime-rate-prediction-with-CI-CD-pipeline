import os
import sys

import numpy as np 
import pandas as pd
#import dill
import pickle
import pymongo
import certifi
import logging
from pymongo.write_concern import WriteConcern
from datetime import datetime
from meteostat import Point, Daily
from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV

from src.exception import CustomException

def save_object(file_path, obj):
    try:
        dir_path = os.path.dirname(file_path)

        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)

    except Exception as e:
        raise CustomException(e, sys)
    
def evaluate_models(X_train, y_train,X_test,y_test,models,param):
    try:
        report = {}

        for i in range(len(list(models))):
            model = list(models.values())[i]
            para=param[list(models.keys())[i]]

            gs = GridSearchCV(model,para,cv=3)
            gs.fit(X_train,y_train)

            model.set_params(**gs.best_params_)
            model.fit(X_train,y_train)

            #model.fit(X_train, y_train)  # Train model

            y_train_pred = model.predict(X_train)

            y_test_pred = model.predict(X_test)

            train_model_score = r2_score(y_train, y_train_pred)

            test_model_score = r2_score(y_test, y_test_pred)

            report[list(models.keys())[i]] = test_model_score

        return report

    except Exception as e:
        raise CustomException(e, sys)
    
def load_object(file_path):
    try:
        with open(file_path, "rb") as file_obj:
            return pickle.load(file_obj)

    except Exception as e:
        raise CustomException(e, sys)
    




def read_data_from_mongodb(database_name,table_name):
    client = pymongo.MongoClient('mongodb+srv://pjeena:chutiyapa@cluster0.u0qdxzq.mongodb.net/test')
    db = client[database_name]
    table = db[table_name]
    all_records = table.find()
    list_cursor = list(all_records)
    df_db = pd.DataFrame(list_cursor)
    df_db = df_db.drop('_id',axis=1)
    return df_db






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
