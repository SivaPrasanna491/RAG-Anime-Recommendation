import uvicorn
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.exception import CustomException
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from backend.app.services.RAG_init_service import load_retrieval_chain
from backend.app.services.vector_db_service import load_vector_db
from backend.app.routes.anime_routes import anime_router
from backend.app.routes.user_routes import user_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"],  # Expose all headers to frontend
)

@app.on_event("startup")
async def load_pipeline():
    try:
        db = load_vector_db()
        app.state.db = db
        app.state.retrieval_chain = load_retrieval_chain(db)
    except Exception as e:
        raise CustomException(e, sys)

# Include API routers
app.include_router(
    user_router,
    prefix='/api/users',
    tags=['Users']
)
app.include_router(
    anime_router,
    prefix='/api/anime',
    tags=['Anime']
)

# Mount static files (frontend) - serve at root for relative paths to work
frontend_path = Path(__file__).parent.parent / "frontend"

# Serve CSS and JS files
app.mount("/css", StaticFiles(directory=str(frontend_path / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(frontend_path / "js")), name="js")

@app.get("/")
def root(request: Request):
    # Check if user is authenticated with valid token
    token = request.cookies.get("access_token")
    
    if token:
        try:
            # Validate token with Supabase
            from backend.app.utils.supabase_client import client
            user_response = client.auth.get_user(jwt=token)
            
            if user_response.user:
                # Valid token, redirect to dashboard
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url="/home", status_code=302)
        except Exception as e:
            # Invalid token, clear it and show landing page
            print(f"Invalid token: {e}")
            pass
    
    # User not logged in or invalid token, show landing page
    return FileResponse(str(frontend_path / "index.html"))

# Serve HTML pages without .html extension
@app.get("/{page_name}")
def serve_page(page_name: str):
    # Map clean URLs to HTML files
    file_path = frontend_path / f"{page_name}.html"
    if file_path.exists():
        return FileResponse(str(file_path))
    return {"error": "Page not found"}

if __name__=="__main__":
    uvicorn.run(app,host="localhost",port=8000)