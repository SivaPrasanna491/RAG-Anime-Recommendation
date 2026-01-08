import sys
import os
import pandas as pd

from dotenv import load_dotenv
from src.exception import CustomException
from src.logger import logging
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from src.utils import generateDocuments
from langchain_groq import ChatGroq
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate

class DataTransformation:
    def transformFeatures(self, data_path):
        try:
            data = pd.read_csv(data_path, encoding='latin')
            documents = data.apply(generateDocuments, axis=1)
            logging.info("Features combined successfully")
            data['combined_text'] = documents
            
            docs = [Document(page_content=row['combined_text'], metadata={"Demographic": row['Demographics']}) for _, row in data.iterrows()] 
            logging.info("Data frame converted into langchain document done successfully")
            
            logging.info("Divide the converted documents into chunks")
            splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=400)
            logging.info("Chunks created successfully")
            
            logging.info("Creating the vector embeddings and storing the embeddings in db")
            embeddings = OllamaEmbeddings(model='bge-m3:567m')
            db = FAISS.from_documents(documents=docs[:128], embedding=embeddings)
            logging.info("Vector embeddingsa and stored successfully")
            db.save_local("artifacts/faiss_index")
        except Exception as e:
            raise CustomException(e, sys)
        