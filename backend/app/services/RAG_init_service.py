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
    url: str = Field(description="Image URL of the anime from the context")
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
            You have access to a comprehensive anime database with titles, genres, themes, episodes, and ratings.

            Your task:
            1) **Analyze the user's query** to identify:
               - Title keywords or specific anime names
               - Genres (Action, Romance, Comedy, Drama, Fantasy, Sci-Fi, Horror, etc.)
               - Themes (School, Ninja, Magic, Sports, Supernatural, Mecha, etc.)
               - Episode count preferences (short series, long series, specific numbers)
               - Any combination of the above criteria

            2) **Intelligent categorization**:
               - If user provides values without labels (e.g., "action ninja 200 episodes"):
                 * Automatically identify "action" as genre
                 * Automatically identify "ninja" as theme
                 * Automatically identify "200 episodes" as episode count
               - Match anime that satisfy ALL provided criteria when possible
               - If user specifies feature names explicitly, use them as filters

            3) **Smart matching strategy**:
               - **Multiple criteria**: Find anime matching ALL criteria (genre AND theme AND episodes)
               - **Partial matches**: If no exact matches, find anime matching most criteria
               - **Similar alternatives**: Recommend similar anime if exact matches are limited
               - **Prioritize**: Exact matches first, then close matches, then similar alternatives

            4) **NEVER say you couldn't find anything**:
               - Always provide 5-10 relevant recommendations
               - If exact matches don't exist, recommend closest alternatives
               - Explain why alternatives are good matches

            5) **Response requirements**:
               - Recommend 5-10 anime (more if highly relevant)
               - For each: Title, Genre, Theme, Episodes, Rating, Brief Description
               - Explain why each matches the user's criteria
               - Order by relevance (best matches first)

            6) **Critical rules**:
               - Extract exact titles and genres from the context documents
               - NEVER hallucinate or make up anime that don't exist in context
               - Only use information from provided context
               - Base ALL recommendations on context documents

            Be conversational, enthusiastic, and helpful!'''

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