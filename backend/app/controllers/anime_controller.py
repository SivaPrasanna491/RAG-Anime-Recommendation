import os
import sys

from src.exception import CustomException
from src.logger import logging
from backend.app.utils.supabase_client import client
from fastapi import Cookie, Header, HTTPException
from fastapi import Request
from src.utils import generateImage

def generateRecommendations(payload, request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return {"message": "User not authenticated"}
        retrieval_chain = request.app.state.retrieval_chain
        logging.info(f"Generating recommendations for query: {payload.query}")
        
        response = retrieval_chain.invoke(payload.query)
        
        logging.info(f"LLM Response: {response}")
        print(f"LLM response: {response}")
        
        return {
            "message": response.message,
            "recommendations": [
                {
                    "title": rec.title,
                    "genre": rec.genre,
                    "url": rec.url,
                    "reason": rec.reason
                }
                for rec in response.recommendations
            ],
        }
            
    except Exception as e:
        raise CustomException(e, sys)
    
def getAnime(payload, request):
    try:
        token = request.cookies.get("access_token")

# Or get from header
        if not token:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user_response = client.auth.get_user(jwt=token)
        result = (
            client.tables("animes")
            .insert({"anime_name": payload.title, "anime_genre": payload.genre})
            .execute()
        )
        if result.error:
            raise Exception(result.error.message)
        result = (
            client.table("users")
            .select("user_id")
            .eq("email", user_response.user.email)
            .execute()
        )
        user_id = result.data[0]['user_id']
        result = (
            client.table("animes")
            .select("anime_id")
            .eq("anime_name", payload.title)
            .execute()
        )
        anime_id = result.data[0]['anime_id']
        result = (
            client.table("useranimeinteractions")
            .insert({"user_id": user_id, "anime_id": anime_id, "interaction_type": "view"})
            .execute()
        )
        if result.error:
            raise Exception(result.error.message)
        return {"message": "Anime viewed successfully"}
    except Exception as e:
        raise CustomException(e, sys)