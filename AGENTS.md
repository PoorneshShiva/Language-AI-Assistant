# Repository Guidelines

## Project Structure & Module Organization
- `src/lexilearn/` contains the FastAPI backend with subpackages `database/`, `graph_nodes/`, `graphql/`, `rest/`, and `utils/agents/`; the entrypoint is `main.py`.
- `frontend/` is a Create React App; shared UI lives in `frontend/src/components/`, and API helpers in `frontend/src/api.js`.
- `tests/` hosts backend pytest suites and fixtures in `tests/models/`; SQLite seed data ships in `lexilearn.db`.
- Reference material stays in `docs/` and `notebooks/`, while runtime logs belong under `logs/`.

## Build, Test, and Development Commands
- `poetry install` resolves Python (>=3.12) dependencies from `pyproject.toml`.
- `poetry run lexilearn --host 127.0.0.1 --port 8000` serves the API; add `--reload` locally for auto-restarts.
- `poetry run pytest` runs backend tests; narrow scope with `-k name` during iteration.
- From `frontend/`, run `npm install`, `npm start` for the dev server, and `npm run build` for production bundles.
- `./start.sh` launches backend and frontend together for end-to-end checks.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indents, docstrings, and type hints; mirror the patterns in `src/lexilearn/main.py`.
- Modules stay `snake_case`; classes and React components use `PascalCase`; functions, hooks, and variables use `camelCase`.
- CRA’s default ESLint rules run via `npm start`/`npm test`; resolve warnings before pushing.
- Keep logging consistent with the Loguru setup in `src/lexilearn/config/config.py`.

## Testing Guidelines
- Create backend tests alongside features as `tests/test_<feature>.py`; extend fixtures in `tests/models/` when schema changes.
- Stub data through helpers in `lexilearn.database` instead of mutating `lexilearn.db` directly.
- Frontend tests rely on React Testing Library (`npm test`); colocate specs as `<Component>.test.js` within `frontend/src/`.

## Commit & Pull Request Guidelines
- Write focused commits in the imperative mood, following history such as `chore: Update file structure according to graphql`.
- Use Conventional Commit prefixes (`feat`, `fix`, `chore`, `docs`) when helpful and keep subject lines under ~72 characters.
- PRs should describe scope, list verification steps (`pytest`, `npm test`, manual UI), link related issues, and attach screenshots or sample queries when UX or schema changes are visible.

## Environment & Configuration
- Secrets for Google, Ollama, or Hugging Face belong in a local `.env`; `lexilearn/utils/agents/model.py` loads them with `python-dotenv`.
- Do not commit `.env` files or raw keys; document expected variable names instead.
- Logs roll to `logs/file_<time>.log`; add new sinks through `src/lexilearn/config/config.py` when needed.
