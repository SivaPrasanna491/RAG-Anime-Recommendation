import os
import sys
import requests

from pydantic import BaseModel
from fastapi import APIRouter, Request
from src.exception import CustomException
from src.logger import logging
from backend.app.utils.supabase_client import client
from backend.app.controllers.user_controller import signup_user, login_user, logout, homePage, delete_user
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
        # Return the full result (message, access_token, email_verification_required)
        response = JSONResponse(content=result)
        
        # Only set cookie if access_token exists (no email verification required)
        print(f"Signup result: {result}")
        if 'access_token' in result:
            response.set_cookie(
                key="access_token",
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
        response = JSONResponse(content=result)
        
        print(f"Login message: {result['message']}")
        # Only set cookie if access_token exists
        if 'access_token' in result:
            response.set_cookie(
                key="access_token",
                value=result['access_token'],
                httponly=True,
                max_age=3600,
                samesite="lax"
            )
        
        return response
    except Exception as e:
        raise CustomException(e, sys)


@user_router.post("/logout")
def logout_route():  # ← Renamed to avoid conflict
    try:
        result = logout()  # ← Now calls controller function
        response = JSONResponse(content={"message": result['message']})
        # Clear the token cookie (not access_token!)
        response.delete_cookie(key="access_token")  # ← Fixed: "token" not "access_token"
        return response
    except Exception as e:
        raise CustomException(e, sys)
    
@user_router.get("/home")
def home(request:Request):
    try:
        result = homePage(request=request)
        return JSONResponse(content=result['message'])
    except Exception as e:
        raise CustomException(e, sys)

@user_router.delete("/delete")
def delete(request: Request):
    """Delete user account from both users table and Supabase Auth"""
    try:
        result = delete_user(request=request)
        response = JSONResponse(content={"message": result['message']})
        # Clear the cookie
        response.delete_cookie(key="token")
        return response
    except Exception as e:
        raise CustomException(e, sys)
