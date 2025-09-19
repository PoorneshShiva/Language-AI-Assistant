# Gemini AI Assistant - German Tutor

This document provides instructions on how to run the German Tutor application.

## Prerequisites

-   Python 3.12+
-   Poetry
-   Node.js and npm

## Installation

1.  **Backend:**
    ```bash
    poetry install
    ```

2.  **Frontend:**
    ```bash
    cd frontend
    npm install
    ```

## Running the Application

You can run both the backend and frontend servers concurrently using the `start.sh` script.

```bash
./start.sh
```

This will start:
-   The FastAPI backend at `http://127.0.0.1:8000`
-   The React frontend at `http://localhost:3000`

Open `http://localhost:3000` in your browser to use the application.
