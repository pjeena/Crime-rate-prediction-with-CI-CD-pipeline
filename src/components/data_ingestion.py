import sys
import os
from src.exception import CustomException
from src.logger import logging
from src.utils import read_data_from_mongodb
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from dataclasses import dataclass

from src.components.data_transformation import DataTransformation
from src.components.data_transformation import DataTransformationConfig

from src.components.model_trainer import ModelTrainerConfig
from src.components.model_trainer import ModelTrainer

@dataclass
class DataIngestionConfig:
    train_data_path : str = os.path.join('artifacts','train.parquet')
    test_data_path : str = os.path.join('artifacts','test.parquet')
    raw_data_path : str = os.path.join('artifacts','data.parquet')


class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info('Entered the data ingestion method')

        try:
            #df = pd.read_parquet('data/data_for_model_prep.csv')
            df = read_data_from_mongodb(database_name='PoliceIncidents',table_name='data_model_training')
            logging.info('Read the dataset from mongo db')

            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path),exist_ok=True)
            df.to_parquet(self.ingestion_config.raw_data_path)

            logging.info('Train test split initiated')
            train_set, test_set = train_test_split(df,test_size=0.2,random_state=42)

            train_set.to_parquet(self.ingestion_config.train_data_path)
            test_set.to_parquet(self.ingestion_config.test_data_path)

            logging.info('Data ingestion completed')

            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path

            )
        except Exception as e:
            raise CustomException(e,sys)
            

if __name__=="__main__":
    obj=DataIngestion()
    train_data,test_data=obj.initiate_data_ingestion()

    data_transformation=DataTransformation()
    train_arr,test_arr,_=data_transformation.initiate_data_transformation(train_data,test_data)

    modeltrainer=ModelTrainer()
    print(modeltrainer.initiate_model_trainer(train_arr,test_arr))