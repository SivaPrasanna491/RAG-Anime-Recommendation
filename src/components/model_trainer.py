import os
import sys

from src.exception import CustomException
from src.logger import logging

class ModelTraining:
    def generateRecommendations(self, retrieval_chain, query):
        try:
            logging.info("Retrieval chain loaded successfully")
            response = retrieval_chain.invoke(
                {
                    "input": query
                }
            )
            logging.info("Recommendation got successfully")
            return response['answer']
        except Exception as e:
            raise CustomException(e, sys)