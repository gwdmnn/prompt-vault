# Quickstart: Prompt Repository API & UI

**Phase**: 1 — Design & Contracts
**Date**: 2026-02-14

## Prerequisites

- Python 3.12+
- Node.js 20+ and npm
- PostgreSQL 16+
- An LLM API key (Anthropic, OpenAI, or Google Gemini) for prompt evaluations

## Backend Setup

### 1. Create and activate virtual environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### 2. Install dependencies

```bash
pip install -e ".[dev]"
```

The `pyproject.toml` defines the following dependency groups:
- **Core**: fastapi, uvicorn, sqlmodel, alembic, pydantic-settings, langgraph, langchain-anthropic, langchain-openai, langchain-google-genai, httpx
- **Dev**: pytest, pytest-asyncio, httpx (test client), ruff, coverage

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database
DATABASE_URL=postgresql://promptvault:promptvault@localhost:5432/promptvault

# LLM Provider (choose one)
LLM_PROVIDER=anthropic              # or "openai" or "gemini"
ANTHROPIC_API_KEY=sk-ant-...        # if using Anthropic
OPENAI_API_KEY=sk-...               # if using OpenAI
GOOGLE_API_KEY=...                   # if using Google Gemini

# Application
DEBUG=true
LOG_LEVEL=INFO
```

### 4. Set up the database

```bash
# Create the database
createdb promptvault

# Run migrations
alembic upgrade head

# Seed with sample data (10+ prompts across both categories)
python -m app.seed.data
```

### 5. Start the backend server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now available at:
- **API**: http://localhost:8000/api
- **OpenAPI docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/api/health

## Frontend Setup

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Configure API endpoint

The frontend connects to `http://localhost:8000` by default. To customize, create a `.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start the development server

```bash
npm run dev
```

The UI is now available at http://localhost:5173.

## Verify the Setup

### Quick smoke test

1. Open http://localhost:5173 — you should see the prompt list with pre-loaded sample data.
2. Click on any prompt to view its details and version history.
3. Create a new prompt via the "New Prompt" button.
4. Edit a prompt — the version history should show a new version.
5. Trigger an evaluation from the prompt detail page.
6. View the evaluation dashboard at the Dashboard page.

### API smoke test

```bash
# List prompts
curl http://localhost:8000/api/prompts

# Get a specific prompt (use an ID from the list response)
curl http://localhost:8000/api/prompts/{prompt_id}

# Create a prompt
curl -X POST http://localhost:8000/api/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Prompt",
    "content": "You are a helpful assistant that summarizes articles.",
    "category": "task_execution"
  }'

# Trigger evaluation
curl -X POST http://localhost:8000/api/prompts/{prompt_id}/evaluate

# Health check
curl http://localhost:8000/api/health
```

## Running Tests

### Backend

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test categories
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests (requires test DB)
pytest tests/agents/            # Agent tests (mocked LLM)
```

### Frontend

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## Project Commands

### Backend

| Command | Description |
|---------|-------------|
| `uvicorn app.main:app --reload` | Start dev server |
| `alembic upgrade head` | Apply all migrations |
| `alembic revision --autogenerate -m "description"` | Generate new migration |
| `alembic downgrade -1` | Rollback last migration |
| `python -m app.seed.data` | Load seed data |
| `ruff check .` | Run linter |
| `ruff format .` | Format code |
| `pytest` | Run tests |

### Frontend

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server |
| `npm run build` | Production build |
| `npm run preview` | Preview production build |
| `npm test` | Run tests |
| `npm run lint` | Run ESLint |
| `npm run format` | Run Prettier |

## Seed Data Overview

The seed script creates the following sample data:

- **10+ prompts** across both categories:
  - 5+ orchestrator prompts (multi-step workflow coordination)
  - 5+ task execution prompts (single-task completion)
- **Multiple versions** per prompt (at least 2, per SC-006)
- **Realistic content** related to AI agent development (not placeholder text)
- **Pre-run evaluations** on select prompts for dashboard demonstration

## Architecture Overview

```
Browser (React SPA)
    │
    ▼ HTTP/JSON
FastAPI Backend (:8000)
    ├── /api/prompts      → PromptService → PromptRepository → PostgreSQL
    ├── /api/evaluations  → EvaluationService → LangGraph Agent → LLM Provider
    └── /api/health       → DB health check
```

All components run as a single process. The LangGraph evaluation agent
executes in-process with FastAPI, communicating with external LLM APIs
(Anthropic/OpenAI/Gemini) for prompt quality assessment.
