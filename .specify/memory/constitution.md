<!--
  === Sync Impact Report ===
  Version change: 0.0.0 (template) -> 1.0.0
  Modified principles: N/A (initial population)
  Added sections:
    - Principle 1: API-First Design (SOLID + Clean Architecture)
    - Principle 2: Component-Driven UI
    - Principle 3: Test-First Development
    - Principle 4: Type Safety & Validation
    - Principle 5: Observability & Traceability
    - Section: Technical Constraints
    - Section: Development Workflow
    - Governance rules
  Removed sections: None
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ compatible (Constitution Check section exists)
    - .specify/templates/spec-template.md ✅ compatible (no changes needed)
    - .specify/templates/tasks-template.md ✅ compatible (phases align with principles)
  Follow-up TODOs: None
-->

# PromptVault Constitution

## Core Principles

### I. API-First Design (SOLID + Clean Architecture)

Every backend feature MUST start from its API contract (OpenAPI schema)
before any implementation begins. The FastAPI backend MUST follow
SOLID principles and layered architecture:

- **Single Responsibility**: Each module (route, service, model, agent)
  MUST own exactly one concern. Routes handle HTTP; services handle
  business logic; models handle data; agents handle LLM orchestration.
- **Open/Closed**: New evaluation criteria, prompt types, or agent
  strategies MUST be addable without modifying existing service code.
  Use dependency injection and strategy patterns.
- **Liskov Substitution**: All LLM provider integrations (Anthropic,
  OpenAI) MUST be interchangeable behind a common interface.
- **Interface Segregation**: Clients MUST NOT depend on methods they
  do not use. Keep Pydantic schemas purpose-specific (create, update,
  response) rather than reusing a single monolithic model.
- **Dependency Inversion**: Services MUST depend on abstractions (protocols/ABCs),
  not concrete implementations. Database access MUST go through a repository
  layer; LLM calls MUST go through a provider abstraction.

The project structure MUST enforce clear separation:
`api/` (routes) -> `services/` (logic) -> `models/` (data) with
`agents/` as a parallel domain for LangGraph orchestration.

### II. Component-Driven UI

The React + TypeScript frontend MUST follow modern React best practices:

- **Functional components only** with hooks for state and side effects.
  Class components MUST NOT be introduced.
- **Single Responsibility per component**: Each component MUST do one
  thing. Container components handle data fetching; presentational
  components handle rendering. Place related files (component,
  styles, tests, types) in the same directory.
- **Immutable state**: Use React state and context correctly. State
  MUST flow top-down. Side effects MUST live in `useEffect` or custom
  hooks. Shared state MUST use context or a lightweight state manager
  only when prop drilling exceeds 3 levels.
- **Type everything**: All props, state, API responses, and event
  handlers MUST have explicit TypeScript types. `any` is forbidden
  except in third-party type workarounds (documented with a comment).
- **Tailwind-first styling**: Use Tailwind CSS utility classes. Custom
  CSS MUST only be introduced for animations or third-party component
  overrides. No inline style objects unless dynamically computed.
- **Accessible by default**: Interactive elements MUST use semantic
  HTML. Forms MUST have labels. ARIA attributes MUST be added when
  semantic HTML is insufficient.

### III. Test-First Development

Automated testing is mandatory for all backend business logic and
critical frontend flows:

- **Backend**: Every service function and API endpoint MUST have at
  least one unit test and one integration test before the feature is
  considered complete. Use pytest with async support.
- **Frontend**: Critical user journeys (prompt submission, evaluation
  results display) MUST have component tests. Use React Testing
  Library; test behavior, not implementation details.
- **Agent evaluation**: LangGraph agent flows MUST have deterministic
  integration tests using mocked LLM responses to verify state
  transitions and output structure.
- **Red-Green-Refactor**: When TDD is applied, tests MUST be written
  first, verified to fail, then implementation proceeds. Refactoring
  MUST NOT change test assertions.
- **Coverage target**: Backend MUST maintain >= 80% line coverage on
  `services/` and `api/` directories. Frontend coverage is encouraged
  but not gated.

### IV. Type Safety & Validation

Data integrity MUST be enforced at every system boundary:

- **API layer**: All request/response payloads MUST be validated by
  Pydantic models (via FastAPI). No raw dict manipulation in route
  handlers.
- **Database layer**: SQLModel MUST be used for all database entities.
  Migrations MUST be managed through Alembic with no manual schema
  changes.
- **Frontend layer**: API client functions MUST return typed
  interfaces. Use TypeScript strict mode (`strict: true` in
  tsconfig). Zod or similar runtime validation MUST be applied to
  API responses when the backend is not fully trusted (e.g., external
  APIs).
- **Agent layer**: LangGraph state schemas MUST be typed. Agent
  inputs and outputs MUST conform to Pydantic models.
- **No implicit conversions**: Avoid `# type: ignore` and TypeScript
  `as` casts unless documented with a justification comment.

### V. Observability & Traceability

Every system action MUST be traceable for debugging and auditing:

- **Structured logging**: Use Python `logging` with JSON format in
  production. Every log entry MUST include a correlation/request ID.
- **Agent tracing**: LangGraph executions MUST be instrumented via
  LangSmith (or equivalent) for step-by-step observability of
  evaluation runs.
- **API documentation**: FastAPI auto-generated OpenAPI docs MUST be
  kept accurate. Every endpoint MUST have a summary, description,
  and response model.
- **Error responses**: All API errors MUST return structured JSON with
  `detail`, `code`, and optional `field` for validation errors.
  Stack traces MUST NOT leak to clients in production.
- **Health checks**: The API MUST expose a `/health` endpoint
  returning database and critical dependency status.

## Technical Constraints

Stack decisions per ADR-001 are binding for the MVP:

| Layer | Technology | Constraint |
|-------|-----------|------------|
| Backend | Python 3.12+ / FastAPI | Async-first; Pydantic v2 |
| Agent | LangGraph 0.2+ | Runs in-process with FastAPI |
| Frontend | React 19+ / TypeScript 5.5+ / Vite 6+ | Functional components only |
| Styling | Tailwind CSS 4+ | Utility-first; minimal custom CSS |
| Database | PostgreSQL 16+ / SQLModel | JSONB for agent outputs |
| Migrations | Alembic 1.14+ | All schema changes via migrations |

Additional constraints:
- **No premature microservices**: The MVP MUST remain a monolith
  (FastAPI + LangGraph in one process). Service extraction is a
  post-MVP decision.
- **Environment config**: All secrets and configuration MUST come
  from environment variables or `.env` files. No hardcoded
  credentials.
- **Dependency management**: Backend uses `pyproject.toml` with
  pinned dependencies. Frontend uses `package.json` with a lockfile.
  Dependencies MUST be reviewed before adding (no bloat).

## Development Workflow

All contributors (human and AI agents) MUST follow this workflow:

- **Branch strategy**: One branch per feature/fix. Branch names
  follow `###-feature-name` convention. Merge to `main` via PR.
- **Commit discipline**: Commits MUST be atomic and use conventional
  commit messages (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
- **Code review gate**: No code merges to `main` without at least
  one review pass (human or automated). PRs MUST include a
  description of changes and testing done.
- **Linting and formatting**: Backend MUST pass `ruff` checks.
  Frontend MUST pass `eslint` + `prettier`. These checks MUST run
  in CI before merge.
- **Database migrations**: Every model change MUST include an Alembic
  migration. Migrations MUST be reviewed for data safety (no
  destructive operations without explicit approval).
- **API versioning**: Breaking API changes MUST NOT be introduced
  without a deprecation period or version bump. For MVP, the API
  operates unversioned; versioning MUST be introduced before any
  public release.

## Governance

This constitution is the authoritative source of engineering
standards for PromptVault. All design decisions, code reviews,
and implementation plans MUST verify compliance with these
principles.

- **Amendments**: Any change to this constitution MUST be
  documented with rationale, approved by the project lead, and
  accompanied by a migration plan for existing code that violates
  the new rule.
- **Versioning**: The constitution follows semantic versioning.
  MAJOR for principle removals/redefinitions, MINOR for new
  principles or material expansions, PATCH for clarifications.
- **Compliance review**: Every PR MUST be checked against
  applicable principles. The plan-template Constitution Check
  gate MUST be passed before implementation begins.
- **Exceptions**: Violations MUST be documented in the plan's
  Complexity Tracking table with justification and rejected
  alternatives.

**Version**: 1.0.0 | **Ratified**: 2026-02-14 | **Last Amended**: 2026-02-14
