import os
import sys
from typing import List
from pydantic import BaseModel, Field

from dotenv import load_dotenv
from src.exception import CustomException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()  

class AnimeRecommendation(BaseModel):
    """Single anime recommendation"""
    title: str = Field(description="Exact anime title from the context")
    genre: str = Field(description="Genre of the anime from the context")
    reason: str = Field(description="Brief reason why this anime matches the user's query (1 sentence)")

class RecommendationResponse(BaseModel):
    """Complete recommendation response"""
    message: str = Field(description="A brief, friendly message about the recommendations (1-2 sentences)")
    recommendations: List[AnimeRecommendation] = Field(description="List of 5-10 anime recommendations")

def load_retrieval_chain(db):
    try:
        base_llm = ChatGoogleGenerativeAI(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model='gemini-2.5-flash',
            temperature=0.3,  # Lower temperature for consistent structured output
            max_retries=3
        )
        
        llm = base_llm.with_structured_output(RecommendationResponse)
        
        system_prompt = '''You are an expert AI assistant specialized in recommending anime to users.

            Your task:
            1) Analyze the user's query to understand what they're looking for (genre, theme, title, episodes, etc.)
            2) Search through the provided context documents to find matching animes
            3) If exact matches aren't found, recommend similar animes based on genre, theme, or characteristics
            4) NEVER say you couldn't find anything - always provide the closest matches
            5) Recommend 5-10 animes based on relevance
            6) Extract the exact title and genre from the context for each recommendation
            7) NEVER hallucinate - only recommend animes that exist in the provided context
            8) Only use information from the context provided

            Important: Base all recommendations on the context documents provided. Do not make up anime titles.'''

        human_message = '''Context documents:
            {context}

            User query: {input}

            Provide anime recommendations based on the context above.'''

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_message)
        ])
        
        retriever = db.as_retriever(search_kwargs={"k": 50})
        
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser
        
        retrieval_chain = (
            {
                "context": retriever,
                "input": RunnablePassthrough()
            }
            | prompt
            | llm
        )
        
        return retrieval_chain
        
    except Exception as e:
        raise CustomException(e, sys)