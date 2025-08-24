"""Main module for the LexiLearn FastAPI application.

This module initializes the FastAPI application and defines the main routes.
It also includes the Uvicorn server setup for running the application.
"""
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
import argparse

# GraphQL imports
from strawberry.fastapi import GraphQLRouter
from lexilearn.graphql.schema import schema # Your GraphQL schema

# from lexilearn.routes.graphs import router

# from fastapi.middleware.trustedhost import TrustedHostMiddleware


app = FastAPI()

# Setup GraphQL route
graphql_app = GraphQLRouter(schema, graphiql=True) # graphiql=True enables the interactive UI
app.include_router(graphql_app, prefix="/graphql")

# app.include_router(
#             router,
#             prefix="/g",
#             tags=["graph"])

# app.add_middleware(
#    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"]
# )


@app.get("/")
async def root():
    """Root endpoint for the LexiLearn application.

    Returns:
        str: A welcome message.
    """
    return "Welcome to lexilearn"

def main():
    """Runs the FastAPI application using Uvicorn server.

    Configures and starts the Uvicorn server with specified host, port,
    logging level, request limits, and worker count.
    """
    parser = argparse.ArgumentParser(description="LexiLearn FastAPI application")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--workers", type=int, default=6, help="Number of worker processes")
    args = parser.parse_args()

    uvicorn.run(
            "lexilearn.main:app",
            # "app:app",
            host=args.host,
            port=args.port,
            log_level="info",
            limit_max_requests=1028,
            workers=args.workers,
            # reload=True        # Enable auto-reload for development
            )

if __name__ == "__main__":
    main()
