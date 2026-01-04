import os
import sys
import pandas as pd
import time
import requests

from src.exception import CustomException
from src.logger import logging
from dataclasses import dataclass
from jikanpy import Jikan
from src.utils import *


@dataclass
class DataIngestionConfig():
    data_path = os.path.join("artifacts", "data.csv")

class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()
    
    def extract_anime_records(self):
        try:
            limit_pages = 20
            anime_data = []
            # jikan = Jikan(selected_base="https://api.jikan.moe/v4")
            for page in range(1, limit_pages + 1):
                print(f"Fetching page: {page}")
                response = requests.get(f"https://api.jikan.moe/v4/top/anime?page={page}")
                if response.status_code == 200:
                    anime_data.extend(response.json()['data'])
                else:
                    print(f"Error fetching page {page}: {response.status_code}")
                time.sleep(1.5)   
            return anime_data
        except Exception as e:
            raise CustomException(e, sys)
    
    def extract_necessary_records(self):
        try:
            data = self.extract_anime_records()
            titles = extract_features_by_name(data=data, feature_name="titles")
            genres = extract_features_by_name(data=data, feature_name="genres")
            themes = extract_features_by_name(data=data, feature_name="themes")
            demographics = extract_features_by_name(data=data, feature_name="demographics")
            ids = extract_features(data=data, feature_name="mal_id")
            episodes = extract_features(data=data, feature_name="episodes")
            
            logging.info("Features extracted successfully")
            
            df = pd.DataFrame(
                {
                    "Id": ids,
                    "Title": titles,
                    "Genres": genres,
                    "Themes": themes,
                    "Demographics": demographics,
                    "Episodes": episodes
                }
            )
            logging.info("Features converted into .csv format successfully")
            os.makedirs(os.path.dirname(self.ingestion_config.data_path), exist_ok=True)
            df.to_csv(self.ingestion_config.data_path,index=False,header=True)
            return (
                df
            )
        except Exception as e:
            raise CustomException(e, sys)
        
if __name__=="__main__":
    obj = DataIngestion()
    print(obj.extract_necessary_records())
