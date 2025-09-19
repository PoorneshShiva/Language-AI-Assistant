# Language Learner AI Assistant - lexilearn

## Description

The Language Learner AI Assistant is designed to be an effective and agentic learning tool for language students. Initially focused on German, the project aims to provide a personalized learning experience with the potential to scale to other languages in the future.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

Get started with the Language Learner AI Assistant by following the instructions below.

### Prerequisites

- Python 3.12+
- Poetry
- Node.js and npm
- MongoDB

### Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/PoorneshShiva/Language-AI-Assistant
    cd Language-AI-Assistant
    ```

2.  **Backend Setup**

    ```bash
    poetry install
    ```

3.  **Frontend Setup**

    ```bash
    cd frontend
    npm install
    ```

## Usage

You can run both the backend and frontend servers concurrently using the `start.sh` script from the root of the project.

```bash
./start.sh
```

This will start:
- The FastAPI backend at `http://127.0.0.1:8000`
- The React frontend at `http://localhost:3000`

Open `http://localhost:3000` in your browser to use the application.

## Architecture

The application is built with a modern backend and a flexible API design to support a rich, interactive frontend.

-   **Backend:** The backend is built with **FastAPI**, a modern, fast (high-performance) web framework for building APIs with Python 3.12+.

-   **Database:** We use **MongoDB** as our primary database. It stores all application data, including:
    -   `words`: A collection for storing detailed grammatical information about German words (verbs, nouns, adjectives), including translations, conjugations, declensions, and examples.
    -   `user_submissions`: Stores the raw sentences submitted by users.
    -   `user_word_progress`: Tracks each user's learning progress for each word, including their spaced repetition schedule, confidence level, and learning history.

-   **API:** The application uses a hybrid API approach:
    -   A **RESTful API** for straightforward actions.
    -   A **GraphQL API** for complex queries and mutations, allowing the frontend to fetch all the data it needs in a single request. This is implemented using `strawberry-graphql`.

-   **Orchestration:** A central `run_pipeline` orchestrator manages the entire learning process, from analyzing a user's sentence to creating learning materials and scheduling reviews.

-   **Agentic System:** The core of the German grammar enrichment is an agentic system built with **LangGraph**. This allows for a flexible and powerful way to process language and generate detailed grammatical insights.

## Key Features

- **Learn from your own sentences:** Submit any German sentence and the system will break it down for you.
- **Detailed Grammatical Enrichment:** Verbs, nouns, and adjectives are extracted and enriched with detailed grammar, including conjugations, declensions, gender, and more.
- **Spaced Repetition System (SRS):** The application uses a spaced repetition algorithm to schedule reviews and help you remember words more effectively.
- **Interactive Lessons:** (Future) The frontend will provide interactive, color-coded lessons based on the enriched grammar data.
- **GraphQL API:** A powerful and flexible API for fetching data and performing actions.

## Contributing to Open-Source

Contributions are welcome! If you have any ideas, improvements, or new apps to add, please create a new [GitHub Issue](https://github.com/PoorneshShiva/Language-AI-Assistant/issues) or submit a pull request.  
Make sure to follow the existing project structure and include a detailed `README.md` for each new app.

## License

This project is licensed under the [MIT License](https://github.com/PoorneshShiva/Language-AI-Assistant/blob/main/LICENSE) — basically, you're free to use, modify, and share it however you like.  
No strings attached... just don't sue us if your computer gains sentience 🤖✨  
Go ahead, build cool stuff with it!