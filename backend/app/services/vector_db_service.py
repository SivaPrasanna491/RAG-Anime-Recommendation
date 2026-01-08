import os
import sys

from src.exception import CustomException
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

def load_vector_db():
    try:
        db = FAISS.load_local("artifacts/faiss_index", OllamaEmbeddings(model='bge-m3:567m'), allow_dangerous_deserialization=True)
        return db
    except Exception as e:
        raise CustomException(e, sys)