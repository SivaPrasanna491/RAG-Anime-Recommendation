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
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTraining

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
            
            for page in range(1, limit_pages + 1):
                print(f"Fetching page: {page}/{limit_pages}")
                
                # Retry logic with exponential backoff
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = requests.get(
                            f"https://api.jikan.moe/v4/top/anime?page={page}",
                            timeout=30  # Add timeout
                        )
                        
                        if response.status_code == 200:
                            anime_data.extend(response.json()['data'])
                            print(f"✓ Page {page} fetched successfully ({len(anime_data)} total anime)")
                            break
                        elif response.status_code == 429:  # Rate limit
                            wait_time = 5 * (attempt + 1)
                            print(f"⚠ Rate limited. Waiting {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            print(f"✗ Error fetching page {page}: {response.status_code}")
                            break
                            
                    except requests.exceptions.Timeout:
                        print(f"⚠ Timeout on page {page}, attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            time.sleep(3 * (attempt + 1))  # Exponential backoff
                        else:
                            print(f"✗ Failed to fetch page {page} after {max_retries} attempts")
                    
                    except requests.exceptions.ConnectionError:
                        print(f"⚠ Connection error on page {page}, attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            time.sleep(5 * (attempt + 1))
                        else:
                            print(f"✗ Failed to fetch page {page} after {max_retries} attempts")
                
                # Respect rate limit: 3 requests per second = wait 0.4s minimum
                time.sleep(2)  # Increased to 2 seconds to be safe
                
            print(f"\n✓ Total anime fetched: {len(anime_data)}")
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
            urls = generateImage(data=data)
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
                    "Episodes": episodes,
                    "ImageURLS": urls
                }
            )
            logging.info("Features converted into .csv format successfully")
            os.makedirs(os.path.dirname(self.ingestion_config.data_path), exist_ok=True)
            df.to_csv(self.ingestion_config.data_path,index=False,header=True)
            return (
                self.ingestion_config.data_path
            )
        except Exception as e:
            raise CustomException(e, sys)
