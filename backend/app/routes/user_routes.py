import os
import sys
import requests

from pydantic import BaseModel
from fastapi import APIRouter, Request
from src.exception import CustomException
from src.logger import logging
from backend.app.utils.supabase_client import client
from backend.app.controllers.user_controller import signup_user, login_user, logout, homePage
from fastapi.responses import JSONResponse

user_router = APIRouter()

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    gender: str

class LoginRequest(BaseModel):
    email: str
    password: str

@user_router.post("/signup")
def signup(payload: SignupRequest):
    try:
        result = signup_user(payload)
        response = JSONResponse(content={"message": result['message']})
        
        # Only set cookie if access_token exists (no email verification required)
        if 'access_token' in result:
            response.set_cookie(
                key="token",
                value=result['access_token'],
                httponly=True,
                max_age=3600,
                samesite="lax"
            )
        
        return response
    except Exception as e:
        raise CustomException(e, sys)

@user_router.post("/login")
def login(payload: LoginRequest):
    try:
        result = login_user(payload)
        response = JSONResponse(content={"message": result['message']})
        
        # Only set cookie if access_token exists
        if 'access_token' in result:
            response.set_cookie(
                key="token",
                value=result['access_token'],
                httponly=True,
                max_age=3600,
                samesite="lax"
            )
        
        return response
    except Exception as e:
        raise CustomException(e, sys)
@user_router.post("/logout")
def logout():
    try:
        result = logout()
        return JSONResponse(content=result['message'])
    except Exception as e:
        raise CustomException(e, sys)
    
@user_router.get("/home")
def home(request:Request):
    try:
        result = homePage(request=request)
        return JSONResponse(content=result['message'])
    except Exception as e:
        raise CustomException(e, sys)

