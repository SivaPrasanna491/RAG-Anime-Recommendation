import os
import sys

from src.components.data_ingestion import DataIngestion
from src.components.data_transformation import DataTransformation

if __name__=="__main__":
    ingestionObj = DataIngestion()
    path = ingestionObj.extract_necessary_records()
    
    transformationObj = DataTransformation()
    transformationObj.transformFeatures(data_path=path)