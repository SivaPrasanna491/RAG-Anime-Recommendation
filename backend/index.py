import uvicorn
import sys

from fastapi import FastAPI, Request
from src.exception import CustomException
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from backend.app.services.RAG_init_service import load_retrieval_chain
from backend.app.services.vector_db_service import load_vector_db
from backend.app.routes.anime_routes import anime_router
from backend.app.routes.user_routes import user_router

app = FastAPI()

@app.on_event("startup")
async def load_pipeline():
    try:
        db = load_vector_db()
        app.state.db = db
        app.state.retrieval_chain = load_retrieval_chain(db)
    except Exception as e:
        raise CustomException(e, sys)

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

@app.get("/")
def root():
    return {"status": "Server running"}

if __name__=="__main__":
    uvicorn.run(app,host="localhost",port=8000)