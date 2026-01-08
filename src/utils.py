import os
import sys

from src.exception import CustomException
from src.logger import logging

def extract_features_by_name(data, feature_name):
    try:
        result = []
        for i in range(0, len(data)):
            values = data[i][feature_name]
            value = []
            if feature_name == "genres" or feature_name == "themes" or feature_name == "demographics":
                if len(values) == 0:
                    result.append(['Unknown'])
                else:
                    for j in range(0, len(values)):
                        value.append(values[j]['name'])
                    result.append(value)
                    
            elif feature_name == "titles":
                for j in range(0, len(values)):
                    value.append(values[j]['title'])
                result.append(value)
        return result
    except Exception as e:
        raise CustomException(e, sys)

def extract_features(data, feature_name):
    try:
        result = []
        for i in range(0, len(data)):
            result.append(data[i][feature_name])
        return result
    except Exception as e:
        raise CustomException(e, sys)


def generateDocuments(row):
    try:
        titles = ", ".join(map(str, row['Title']))
        genres = ", ".join(map(str, row['Genres']))
        themes = ", ".join(map(str, row['Themes']))
        
        return f"""
                Id: {row['Id']}
                Title: {titles}
                Genre: {genres}
                Theme: {themes}
                Episodes: {row['Episodes']}
    """.strip()
    except Exception as e:
        raise CustomException(e, sys)