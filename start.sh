#!/bin/bash

# Start the backend
echo "Starting backend..."
poetry run lexilearn &
BACKEND_PID=$!

# Start the frontend
echo "Starting frontend..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!

# Wait for both processes to exit
wait $BACKEND_PID
wait $FRONTEND_PID
