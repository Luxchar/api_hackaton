from contextlib import asynccontextmanager
from config import Config
from fastapi import FastAPI
from pymongo import MongoClient

from routes.router import router
from routes.get.router import getrouter
from routes.post.router import postrouter
from routes.user.router import userrouter

config = Config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for database connection"""
    app.mongodb_client = config.client
    app.database = config.db
    yield
    app.mongodb_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(router, prefix="/api")
app.include_router(getrouter, prefix="/api/get")
app.include_router(postrouter, prefix="/api/post")
app.include_router(userrouter, prefix="/api/user")