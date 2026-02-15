# Implementation Plan: Prompt Repository API & UI

**Branch**: `001-prompt-repository-api` | **Date**: 2026-02-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-prompt-repository-api/spec.md`

## Summary

Build a full-stack prompt repository with version control, automated LLM-based evaluation, and category-based organization. The backend is a Python/FastAPI monolith with LangGraph-powered evaluation agents, PostgreSQL storage via SQLModel, and Alembic migrations. The frontend is a React 19 + TypeScript SPA built with Vite and Tailwind CSS. The system supports CRUD operations on prompts with automatic versioning, prompt quality evaluation against six predefined criteria, and a category-filtered evaluation dashboard. Pre-populated seed data enables immediate exploration.

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.5+ (frontend)
**Primary Dependencies**: FastAPI 0.115+, SQLModel 0.0.22+, LangGraph 0.2+, Alembic 1.14+, Pydantic v2, React 19+, Vite 6+, Tailwind CSS 4+, TanStack Query (React Query) for server state
**Storage**: PostgreSQL 16+ via SQLModel ORM; JSONB for flexible agent metadata; Alembic for migrations
**Testing**: pytest with async support + httpx (backend); React Testing Library + Vitest (frontend); mocked LLM responses for agent tests
**Target Platform**: Web application — Linux server (backend), modern browsers (frontend)
**Project Type**: Web application (separate backend + frontend directories)
**Performance Goals**: API responses < 2s (list/filter), < 3s (create/update), evaluation completion < 60s
**Constraints**: Monolithic architecture (FastAPI + LangGraph in-process), no authentication for MVP, single-user, max prompt length 50,000 characters
**Scale/Scope**: Single-user MVP, ~10 seed prompts, 2 fixed categories, 6 fixed evaluation criteria
**UI Design**: Modern and minimalist interface optimized for software engineers. Clean layouts with generous whitespace, monospace font for prompt content, syntax-aware rendering, and clear visual hierarchy. Navigation must be fast and keyboard-friendly. Prompt data (content, versions, evaluation scores, categories) must be scannable at a glance without unnecessary chrome or decoration.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Notes |
|---|-----------|--------|-------|
| I | API-First Design (SOLID + Clean Architecture) | PASS | OpenAPI contracts defined before implementation. Layered architecture: `api/` -> `services/` -> `models/` with `agents/` parallel domain. Repository pattern for DB access. Strategy pattern for LLM providers. |
| II | Component-Driven UI | PASS | React 19 + TypeScript, functional components only, Tailwind CSS, container/presentational split, typed props and API responses. |
| III | Test-First Development | PASS | pytest + httpx for backend API/service tests. React Testing Library + Vitest for frontend. Mocked LLM for agent integration tests. >= 80% coverage target on services/ and api/. |
| IV | Type Safety & Validation | PASS | Pydantic v2 models for all API payloads. SQLModel for DB entities. TypeScript strict mode. TanStack Query for typed server state. |
| V | Observability & Traceability | PASS | Structured JSON logging with correlation IDs. LangSmith integration for agent tracing. Auto-generated OpenAPI docs. Structured error responses. `/health` endpoint. |
| — | Technical Constraints | PASS | Stack matches ADR-001 exactly. Monolith architecture. Env-based config. pyproject.toml + package.json with lockfiles. |
| — | Development Workflow | PASS | Feature branch `001-prompt-repository-api`. Conventional commits. Ruff (backend) + ESLint/Prettier (frontend). Alembic migrations for all schema changes. |

**Pre-Phase 0 gate result: PASS** — No violations.

### Post-Phase 1 Re-check

| # | Principle | Status | Design Artifact Verification |
|---|-----------|--------|------------------------------|
| I | API-First Design | PASS | OpenAPI 3.1 contract at `contracts/openapi.yaml` with 13 endpoints. Layered structure confirmed in plan: `api/` -> `services/` -> `repositories/` -> `models/`. LLM provider abstraction via Protocol in `agents/provider.py`. Separate `schemas/` from `models/` (Interface Segregation). |
| II | Component-Driven UI | PASS | Component tree defined: container pages in `pages/`, presentational components in `components/`. TanStack Query hooks in `hooks/`. Types in `types/`. Functional-only, Tailwind-first. |
| III | Test-First Development | PASS | Test structure defined: `tests/unit/`, `tests/integration/`, `tests/agents/`. Mocked LLM strategy documented in research.md. Coverage target >= 80% on services/ and api/. |
| IV | Type Safety & Validation | PASS | Data model defines all Pydantic schemas, SQLModel entities, TypeScript interfaces, and validation rules. TypedDict for LangGraph state. `lock_version` for concurrency. |
| V | Observability & Traceability | PASS | `/api/health` endpoint in contract. Structured error responses (`ErrorResponse` schema). LangSmith tracing planned for agent. Correlation IDs in logging config. |

**Post-Phase 1 gate result: PASS** — All design artifacts comply with constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-prompt-repository-api/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── openapi.yaml     # OpenAPI 3.1 specification
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependency injection (DB session, services)
│   │   ├── prompts.py           # Prompt CRUD + version endpoints
│   │   ├── evaluations.py       # Evaluation trigger + results endpoints
│   │   └── health.py            # Health check endpoint
│   ├── models/
│   │   ├── __init__.py
│   │   ├── prompt.py            # Prompt + PromptVersion SQLModel entities
│   │   ├── evaluation.py        # Evaluation + EvaluationCriterion entities
│   │   └── enums.py             # PromptCategory, EvaluationStatus enums
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── prompt.py            # Pydantic request/response schemas for prompts
│   │   └── evaluation.py        # Pydantic schemas for evaluations
│   ├── services/
│   │   ├── __init__.py
│   │   ├── prompt_service.py    # Prompt business logic (CRUD, versioning)
│   │   └── evaluation_service.py # Evaluation orchestration
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── prompt_repo.py       # Prompt DB access
│   │   └── evaluation_repo.py   # Evaluation DB access
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── evaluator.py         # LangGraph evaluation agent graph
│   │   ├── criteria.py          # Evaluation criteria definitions
│   │   └── provider.py          # LLM provider abstraction (protocol)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings from env vars (pydantic-settings)
│   │   ├── database.py          # DB engine + session factory
│   │   └── logging.py           # Structured JSON logging setup
│   ├── seed/
│   │   ├── __init__.py
│   │   └── data.py              # Seed data definitions + loader
│   └── main.py                  # FastAPI app entrypoint
├── alembic/
│   ├── env.py
│   └── versions/                # Migration files
├── alembic.ini
├── tests/
│   ├── conftest.py              # Fixtures (test DB, client, mocks)
│   ├── unit/
│   │   ├── test_prompt_service.py
│   │   └── test_evaluation_service.py
│   ├── integration/
│   │   ├── test_prompts_api.py
│   │   ├── test_evaluations_api.py
│   │   └── test_health_api.py
│   └── agents/
│       └── test_evaluator.py    # Agent tests with mocked LLM
├── pyproject.toml
└── .env.example

frontend/
├── src/
│   ├── components/
│   │   ├── prompts/
│   │   │   ├── PromptList.tsx
│   │   │   ├── PromptDetail.tsx
│   │   │   ├── PromptForm.tsx
│   │   │   ├── PromptVersionHistory.tsx
│   │   │   └── CategoryFilter.tsx
│   │   ├── evaluations/
│   │   │   ├── EvaluationReport.tsx
│   │   │   ├── EvaluationDashboard.tsx
│   │   │   ├── CriterionScore.tsx
│   │   │   └── ImprovementSuggestions.tsx
│   │   └── shared/
│   │       ├── Layout.tsx
│   │       ├── ErrorBoundary.tsx
│   │       └── LoadingSpinner.tsx
│   ├── pages/
│   │   ├── PromptsPage.tsx
│   │   ├── PromptDetailPage.tsx
│   │   ├── CreatePromptPage.tsx
│   │   ├── EditPromptPage.tsx
│   │   └── DashboardPage.tsx
│   ├── services/
│   │   ├── api.ts               # Axios/fetch client config
│   │   ├── promptService.ts     # Prompt API calls
│   │   └── evaluationService.ts # Evaluation API calls
│   ├── hooks/
│   │   ├── usePrompts.ts        # TanStack Query hooks for prompts
│   │   └── useEvaluations.ts    # TanStack Query hooks for evaluations
│   ├── lib/
│   │   ├── queryClient.ts       # TanStack Query client configuration
│   │   └── queryKeys.ts         # Hierarchical query key factories
│   ├── types/
│   │   ├── prompt.ts            # Prompt, PromptVersion interfaces
│   │   └── evaluation.ts        # Evaluation, Criterion interfaces
│   ├── App.tsx
│   ├── main.tsx
│   └── router.tsx               # React Router configuration
├── tests/
│   ├── components/
│   │   ├── PromptList.test.tsx
│   │   ├── PromptForm.test.tsx
│   │   └── EvaluationReport.test.tsx
│   └── setup.ts
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.ts
└── eslint.config.js
```

**Structure Decision**: Web application structure (Option 2) selected per ADR-001. The `backend/` directory contains the FastAPI monolith with LangGraph agents running in-process. The `frontend/` directory contains the React SPA. The `app/schemas/` directory is separated from `app/models/` to follow Interface Segregation — SQLModel entities (DB) are distinct from Pydantic schemas (API). A `repositories/` layer enforces Dependency Inversion for database access.

### Frontend Hooks Architecture

Hooks serve as the **bridge layer** between the API services and page components. They encapsulate all TanStack Query logic so that components never interact with the query client or cache directly.

**Data flow**: `pages/` (containers) -> `hooks/` (TanStack Query) -> `services/` (API calls) -> Backend

**Layer responsibilities**:

| Layer | Responsibility | React/TQ Awareness |
|-------|---------------|-------------------|
| `services/` | Raw HTTP calls (`fetch`), request/response typing | None — pure async functions, no React imports |
| `lib/queryKeys.ts` | Hierarchical key factories (`promptKeys.detail(id)`, `evaluationKeys.dashboard()`) | None — plain objects with `as const` |
| `lib/queryClient.ts` | `QueryClient` singleton with global defaults (`staleTime`, `gcTime`, `retry`) | TanStack Query only |
| `hooks/` | `useQuery` / `useMutation` wrappers, cache invalidation, optimistic updates | TanStack Query + React |
| `pages/` (containers) | Call hooks, own UI state (filters, modals), pass data down as props | React only |
| `components/` (presentational) | Render data received via props, emit events via callbacks | React only — no hooks from `hooks/` |

**`hooks/usePrompts.ts`** exposes:

| Hook | Purpose | TQ Primitive |
|------|---------|-------------|
| `usePromptList(filters)` | Fetch paginated prompt list with category/search filters | `useQuery` |
| `usePromptDetail(promptId)` | Fetch single prompt with current version content | `useQuery` |
| `usePromptVersions(promptId)` | Fetch version history for a prompt | `useQuery` |
| `usePromptVersion(promptId, versionNumber)` | Fetch a specific version's content | `useQuery` |
| `useCreatePrompt()` | Create prompt, invalidate list cache on success | `useMutation` |
| `useUpdatePrompt(promptId)` | Update prompt, invalidate detail + list + versions cache | `useMutation` |
| `useDeletePrompt()` | Soft-delete prompt, optimistically remove from list cache | `useMutation` |
| `useRestoreVersion(promptId)` | Restore a previous version, invalidate detail + versions | `useMutation` |

**`hooks/useEvaluations.ts`** exposes:

| Hook | Purpose | TQ Primitive |
|------|---------|-------------|
| `useEvaluationDetail(evaluationId)` | Fetch full evaluation report with criteria scores | `useQuery` |
| `useEvaluationDashboard(category?)` | Fetch aggregated scores by category for dashboard | `useQuery` |
| `useTriggerEvaluation(promptId)` | Trigger evaluation, invalidate evaluation + dashboard cache | `useMutation` |

**Key rules**:
- Presentational components (`components/`) MUST NOT import from `hooks/`. They receive data and callbacks as props only, making them testable without mocking TanStack Query.
- Page components (`pages/`) are the only consumers of hooks. They act as containers that wire data to presentational components.
- Cache invalidation happens exclusively inside mutation hooks (`onSuccess` / `onSettled`), never in components.
- For long-running evaluations (up to 60s), the evaluation list query uses `refetchInterval` to poll while any evaluation has `status: "pending"`.

## Complexity Tracking

> No violations detected. Constitution Check passed without exceptions.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
