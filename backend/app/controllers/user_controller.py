import os
import sys

from src.exception import CustomException
from src.logger import logging
from backend.app.utils.supabase_client import client
from fastapi import Cookie, HTTPException

def signup_user(payload):
    try:
        # First check if user already exists in YOUR users table
        existing_user = client.table("users").select("email").eq("email", payload.email).execute()
        
        if existing_user.data and len(existing_user.data) > 0:
            raise HTTPException(status_code=400, detail="Email already registered. Please login instead.")
        
        # Try to sign up with Supabase Auth
        result = client.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
        })
        
        # Check if signup succeeded
        if result.user:
            # Insert into your users table (only if auth signup succeeded)
            client.table("users").insert({
                "name": payload.name,
                "email": payload.email,
                "gender": payload.gender
            }).execute()
            
            # Check if session exists (no email verification)
            if result.session:
                return {
                    "message": "Signup successful", 
                    "access_token": result.session.access_token
                }
            else:
                # User created successfully but needs email verification
                return {
                    "message": "Signup successful! Please check your email to verify your account before logging in.",
                    "email_verification_required": True
                }
        else:
            raise HTTPException(status_code=400, detail="Signup failed")
            
    except Exception as e:
        error_msg = str(e).lower()
        if "already registered" in error_msg or "already exists" in error_msg or "duplicate" in error_msg:
            raise HTTPException(status_code=400, detail="Email already registered. Please login instead.")
        raise CustomException(e, sys)

def login_user(payload):
    try:
        result = client.auth.sign_in_with_password(
            {
                "email": payload.email,
                "password": payload.password
            }
        )
        if result.session:
            return {
                "message": "Login successful", 
                "access_token": result.session.access_token
            }
        else:
            return {
                "message": "Email not found. Please register"
            }
    except Exception as e:
        raise CustomException(e, sys)

def logout():
    try:
        result = client.auth.sign_out()
        if result.error:
            raise Exception(result.error.message)
        return {"message": "User logged out successfully"}
    except Exception as e:
        raise CustomException(e, sys)

def homePage(request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return {"message": "User not authenticated"}
        user_response = client.auth.get_user(jwt=token)
        email = user_response.user.email
        if email is None:
            return {"message": 'User not signed up'}
        return {"message": "User logged in successfully"}
        
    except Exception as e:
        raise CustomException(e, sys)

def delete_user(request):
    """Delete user from both custom users table and Supabase Auth"""
    try:
        # Get token from request
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get user info
        user_response = client.auth.get_user(jwt=token)
        email = user_response.user.email
        user_id = user_response.user.id
        
        # Delete from custom users table
        result = client.table("users").delete().eq("email", email).execute()
        
        # Delete from Supabase Auth
        # Note: This requires admin privileges
        # You need to use the service role key for this
        client.auth.admin.delete_user(user_id)
        
        return {"message": "User deleted successfully"}
        
    except Exception as e:
        raise CustomException(e, sys)