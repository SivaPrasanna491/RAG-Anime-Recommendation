import os
import sys

from fastapi import APIRouter, Cookie, HTTPException, Header
from fastapi import Request
from src.exception import CustomException
from src.logger import logging
from pydantic import BaseModel
from backend.app.controllers.anime_controller import generateRecommendations, getAnime
from fastapi.responses import JSONResponse

anime_router = APIRouter()

class RecommendAnimes(BaseModel):
    query: str
    

class GetAnime(BaseModel):
    title: str
    genre: str


@anime_router.post("/recommendation")
def get_recommendations_route(payload: RecommendAnimes, request: Request):
    try:
        result = generateRecommendations(payload=payload, request=request)
        return JSONResponse(content=result['recommendations'])
    except Exception as e:
        raise CustomException(e, sys)

@anime_router.post("/getAnime")
def get_anime_route(payload: GetAnime, request: Request):  # ✅ Use GetAnime class
    try:
        result = getAnime(payload=payload, request=request)  # ✅ Call controller function
        return JSONResponse(content=result['message'])
    except Exception as e:
        raise CustomException(e, sys)

