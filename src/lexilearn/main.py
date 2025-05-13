
""" Routes for the server """
from typing import Union
from fastapi import FastAPI, Depends
import uvicorn
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.asyncio import (async_sessionmaker,
                                    create_async_engine,
                                    AsyncSession)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from pydantic import BaseModel

# from lexilearn.routes.graphs import router

# from fastapi.middleware.trustedhost import TrustedHostMiddleware


app = FastAPI()

# app.include_router(
#             router,
#             prefix="/g",
#             tags=["graph"])

# app.add_middleware(
#    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"]
# )


@app.get("/")
async def root():
    return "Welcome to lexilearn"

def main():
    uvicorn.run(
            "lexilearn.main:app",
            # "app:app",
            host="127.0.0.1",
            port=8000,
            log_level="info",
            limit_max_requests=1028,
            workers=6,
            # reload=True        # Enable auto-reload for development
            )
