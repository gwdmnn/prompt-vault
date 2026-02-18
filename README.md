# prompt-vault

Prompt repository with version control and LLM-based evaluation. Store, categorize, version, and evaluate AI prompts through a FastAPI backend and React frontend.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (for PostgreSQL)
- Python 3.12+
- Node.js 20+

## Quick Start

### 1. Start the database

```bash
docker compose up -d
```

This starts PostgreSQL 17 on port 5432 and creates two databases:
- `promptvault` — development
- `promptvault_test` — tests

### 2. Set up the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `backend/.env` and set your LLM provider API key:

```
LLM_PROVIDER=anthropic            # or openai, gemini
ANTHROPIC_API_KEY=sk-ant-...
```

The database URL defaults to `postgresql://promptvault:promptvault@localhost:5432/promptvault` and works with the Docker Compose setup out of the box.

### 4. Run database migrations

```bash
cd backend
alembic upgrade head
```

### 5. Seed sample data (optional)

```bash
cd backend
python -m app.seed.data
```

Loads 10 realistic AI agent prompts (5 orchestrator, 5 task execution) with version history.

### 6. Start the backend

```bash
cd backend
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000. Health check: http://localhost:8000/api/health

### 7. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The UI runs at http://localhost:5173. API requests are proxied to the backend automatically.

## Running Tests

```bash
cd backend
pytest
```

Tests use the `promptvault_test` database. The test fixtures create tables at the start of the session and roll back each test's transaction for isolation.

Run with coverage:

```bash
cd backend
coverage run -m pytest && coverage report
```

Frontend tests:

```bash
cd frontend
npm test
```

## Project Structure

```
backend/
  app/
    agents/        # LangGraph evaluation agent, LLM providers, criteria
    api/           # FastAPI route handlers (prompts, evaluations, health)
    core/          # Config, database engine, logging
    models/        # SQLModel entities (Prompt, PromptVersion, Evaluation)
    repositories/  # Database query layer
    schemas/       # Pydantic request/response schemas
    seed/          # Sample data loader
    services/      # Business logic layer
  alembic/         # Database migrations
  tests/
frontend/
  src/
    components/    # React components (prompts, evaluations, shared)
    hooks/         # TanStack Query hooks
    lib/           # Query client, query key factories
    pages/         # Route page components
    services/      # API client and service functions
    types/         # TypeScript interfaces
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/prompts` | List prompts (query: `category`, `search`, `page`, `page_size`) |
| POST | `/api/prompts` | Create a prompt |
| GET | `/api/prompts/{id}` | Get prompt detail |
| PUT | `/api/prompts/{id}` | Update a prompt |
| DELETE | `/api/prompts/{id}` | Soft-delete a prompt |
| GET | `/api/prompts/{id}/versions` | List version history |
| GET | `/api/prompts/{id}/versions/{num}` | Get specific version |
| POST | `/api/prompts/{id}/versions/{num}/restore` | Restore a version |
| POST | `/api/prompts/{id}/evaluate` | Trigger LLM evaluation |
| GET | `/api/evaluations/{id}` | Get evaluation result |
| GET | `/api/evaluations/dashboard` | Aggregated dashboard (query: `category`) |

## Tech Stack

**Backend:** Python 3.12, FastAPI, SQLModel, PostgreSQL, Alembic, LangGraph, Pydantic v2

**Frontend:** React 19, TypeScript, Vite, Tailwind CSS, TanStack Query

**LLM Providers:** Anthropic Claude, OpenAI, Google Gemini (configurable via `LLM_PROVIDER`)
