"""Main module for the LexiLearn FastAPI application.

This module initializes the FastAPI application and defines the main routes.
It also includes the Uvicorn server setup for running the application.
"""
from typing import Union
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
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
import os
import sqlite3
import anyio


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL imports
from strawberry.fastapi import GraphQLRouter
from lexilearn.utils.agents.main import AgenticMain
from lexilearn.graphql.schema import schema # Your GraphQL schema
from lexilearn.rest.api import router as rest_router
from lexilearn.database import Database, get_db_connection

async def get_context():
    conn = get_db_connection() # Get the connection directly
    try:
        agent_main = AgenticMain(conn)
        yield {
            "conn": conn,
            "agent_main": agent_main
        }
    finally:
        conn.close()

# Setup GraphQL route
graphql_app = GraphQLRouter(schema, graphiql=True, context_getter=get_context) # graphiql=True enables the interactive UI
app.include_router(graphql_app, prefix="/graphql")
app.include_router(rest_router, prefix="/api") # Added prefix here

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db_connection = get_db_connection()
        request.state.agent_main = AgenticMain()
        response = await call_next(request)
    finally:
        request.state.db_connection.close()
        request.state.agent_main.close()
    return response


@app.get("/")
async def root():
    """Root endpoint for the LexiLearn application.

    Returns:
        str: A welcome message.
    """
    return "Welcome to lexilearn"

DB_NAME = "lexilearn.db"

def populate_database(db: Database):
    # Add a default user
    db.add_app_user({"id": "test_user", "email": "test@example.com", "display_name": "Test User"})

    # Add some initial data if the database is empty
    # Verbs
    db.add_verb({
        "infinitive": "erklären",
        "present": {"ich": "erkläre", "du": "erklärst", "er/sie/es": "erklärt", "wir": "erklären", "ihr": "erklärt", "sie/Sie": "erklären"},
        "present_perfect": ["hat erklärt"],
        "singular_present_tense": ["erklärt"],
        "simple_past": ["erklärte"],
        "is_separable": False,
        "is_regular": True,
        "english_alternative": ["to explain"]
    })
    db.add_verb({
        "infinitive": "gehen",
        "present": {"ich": "gehe", "du": "gehst", "er/sie/es": "geht", "wir": "gehen", "ihr": "geht", "sie/Sie": "gehen"},
        "present_perfect": ["ist gegangen"],
        "singular_present_tense": ["geht"],
        "simple_past": ["ging"],
        "is_separable": False,
        "is_regular": False,
        "english_alternative": ["to go"]
    })
    # Nouns
    db.add_noun({
        "noun": "Haus",
        "plural": "Häuser",
        "gender": "das",
        "case_forms": {"nominative": "Haus", "accusative": "Haus", "dative": "Haus", "genitive": "Hauses"},
        "english_translation": "house",
        "is_irregular": False
    })
    db.add_noun({
        "noun": "Tisch",
        "plural": "Tische",
        "gender": "der",
        "case_forms": {"nominative": "Tisch", "accusative": "Tisch", "dative": "Tisch", "genitive": "Tisches"},
        "english_translation": "table",
        "is_irregular": False
    })
    db.add_noun({
        "noun": "Jeme",
        "plural": "Jemen",
        "gender": "die",
        "case_forms": {"nominative": "Jeme", "accusative": "Jeme", "dative": "Jeme", "genitive": "Jeme"},
        "english_translation": "Yemen",
        "is_irregular": True
    })

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

    # Initialize and populate database if it doesn't exist
    if not os.path.exists(DB_NAME):
        print(f"Database {DB_NAME} not found. Creating and populating...")
        conn = sqlite3.connect(DB_NAME)
        db = Database(conn)
        db.create_tables()
        populate_database(db)
        conn.close()
        print("Database populated.")

    uvicorn.run(
            "lexilearn.main:app",
            # "app:app",
            host=args.host,
            port=args.port,
            log_level="info",
            limit_max_requests=1028,
            workers=args.workers,
            reload=True        # Enable auto-reload for development
            )

if __name__ == "__main__":
    main()