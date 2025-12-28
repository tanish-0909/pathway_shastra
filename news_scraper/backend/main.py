# main.py

import logging

# Configure logging FIRST before any other imports
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.chats import router as chats_router
from app.routes.versions import router as versions_router
from app.routes import news  # ⬅️ import news router
from app.routes import video  # ⬅️ import video router
from app.database import connect_to_mongo, close_mongo_connection  # ⬅️ import these
from app.services.scheduler import start_scheduler  # ⬅️ video scheduler
from dotenv import load_dotenv
from app.routes.news_search import load_sentiment_model

load_dotenv()  # Load environment variables from .env file
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔌 DB startup/shutdown hooks
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    load_sentiment_model()
    start_scheduler()  # Start video generation scheduler

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Include routers
app.include_router(chats_router)
app.include_router(versions_router)
app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(video.router, prefix="/api/video", tags=["Video"])


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring"""
    return {"status": "healthy", "service": "news-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
