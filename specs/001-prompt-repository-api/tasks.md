# Tasks: Prompt Repository API & UI

**Input**: Design documents from `/specs/001-prompt-repository-api/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: Not included — tests were not explicitly requested in the feature specification. Add test tasks separately if TDD approach is desired.

**Organization**: Tasks are grouped by user story. US1 (CRUD) and US2 (Categories) are combined in one phase because the category field is integral to the Prompt entity and cannot be implemented independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6)
- Exact file paths included in all task descriptions

## User Story → Priority Mapping

| Story | Title | Priority | Phase |
|-------|-------|----------|-------|
| US1 + US2 | Create, Manage & Categorize Prompts | P1 | Phase 3 |
| US6 | Pre-Populated Mock Data | P1 | Phase 4 |
| US3 | Version Control for Prompts | P2 | Phase 5 |
| US4 | Automated Prompt Evaluation | P2 | Phase 6 |
| US5 | View Evaluation Results by Category | P3 | Phase 7 |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency installation, and tooling configuration

- [x] T001 Create backend and frontend directory structure with all packages and `__init__.py` files per plan.md project structure
- [x] T002 Initialize backend Python project with pyproject.toml including all core and dev dependencies (FastAPI, SQLModel, LangGraph, Alembic, pydantic-settings, langchain providers, Ruff, pytest) in backend/pyproject.toml
- [x] T003 [P] Initialize frontend project with package.json, Vite 6, React 19, TypeScript 5.5 strict mode, Tailwind CSS 4, TanStack Query v5, React Router 7, and Vitest in frontend/package.json, frontend/tsconfig.json, frontend/vite.config.ts, and frontend/tailwind.config.ts
- [x] T004 [P] Create backend environment configuration template with database URL, LLM provider settings, and application config in backend/.env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [x] T005 Implement application settings with pydantic-settings (DATABASE_URL, LLM_PROVIDER, API keys, DEBUG, LOG_LEVEL) in backend/app/core/config.py
- [x] T006 Setup database engine and session factory with connection pooling (pool_pre_ping, pool_size=5, max_overflow=10) in backend/app/core/database.py
- [x] T007 [P] Setup structured JSON logging with correlation IDs in backend/app/core/logging.py
- [x] T008 Initialize Alembic configuration with SQLModel metadata discovery and timestamp-based migration naming in backend/alembic.ini and backend/alembic/env.py
- [x] T009 Create FastAPI application entrypoint with CORS middleware, global exception handlers, and router mounting in backend/app/main.py
- [x] T010 Implement dependency injection providers (DB session via yield, service factories) in backend/app/api/deps.py
- [x] T011 [P] Implement health check endpoint with database connectivity test per contracts/openapi.yaml HealthResponse schema in backend/app/api/health.py

### Frontend Foundation

- [x] T012 Create frontend entry point with QueryClientProvider and RouterProvider in frontend/src/main.tsx
- [x] T013 [P] Configure TanStack Query client with global defaults (staleTime, gcTime, retry) in frontend/src/lib/queryClient.ts
- [x] T014 [P] Create API client with base URL configuration and error interceptor in frontend/src/services/api.ts
- [x] T015 [P] Create hierarchical query key factories for prompts and evaluations in frontend/src/lib/queryKeys.ts
- [x] T016 Configure React Router with createBrowserRouter and all application routes in frontend/src/router.tsx
- [x] T017 [P] Create Layout component with navigation header (Prompts, Dashboard links) and main content area in frontend/src/components/shared/Layout.tsx
- [x] T018 [P] Create ErrorBoundary component with fallback UI in frontend/src/components/shared/ErrorBoundary.tsx
- [x] T019 [P] Create LoadingSpinner component in frontend/src/components/shared/LoadingSpinner.tsx

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Stories 1 & 2 — Create, Manage & Categorize Prompts (Priority: P1) 🎯 MVP

**Goal**: Full CRUD operations on prompts with category assignment (orchestrator/task_execution), category filtering, text search, and automatic version creation on content edit. Optimistic concurrency via lock_version.

**Why combined**: US2 (Categories) is implemented as a field on the Prompt entity and a filter parameter on the list endpoint — it cannot be meaningfully separated from US1 (CRUD).

**Independent Test**: Create a prompt with a category, retrieve it, update its content (verify new version created), filter prompt list by category, search by keyword, and soft-delete a prompt.

### Backend Implementation

- [x] T020 [P] [US1] Create PromptCategory and EvaluationStatus enums in backend/app/models/enums.py
- [x] T021 [US1] Create Prompt and PromptVersion SQLModel entities with dual FK relationship, optimistic lock_version, and soft delete flag in backend/app/models/prompt.py
- [x] T022 [US1] Create Pydantic request/response schemas (PromptCreate, PromptUpdate, PromptResponse, PromptDetailResponse, PromptListResponse, PromptVersionResponse) in backend/app/schemas/prompt.py
- [x] T023 [US1] Generate Alembic migration for prompts and prompt_versions tables with indexes (title, category, is_active) and unique constraint (prompt_id, version_number)
- [x] T024 [US1] Implement PromptRepository with CRUD operations, category filtering, ILIKE text search, pagination, and soft delete in backend/app/repositories/prompt_repo.py
- [x] T025 [US1] Implement PromptService with create (auto-version 1), update (new version on content change, lock_version check), soft delete (block if evaluation pending), and list/get operations in backend/app/services/prompt_service.py
- [x] T026 [US1] Implement prompt CRUD and list API endpoints (POST /api/prompts, GET /api/prompts, GET /api/prompts/{id}, PUT /api/prompts/{id}, DELETE /api/prompts/{id}) in backend/app/api/prompts.py

### Frontend Implementation

- [x] T027 [P] [US1] Create TypeScript interfaces for Prompt, PromptVersion, PromptCreate, PromptUpdate, PromptListResponse, and PromptCategory enum in frontend/src/types/prompt.ts
- [x] T028 [US1] Create prompt API service functions (listPrompts, getPrompt, createPrompt, updatePrompt, deletePrompt) in frontend/src/services/promptService.ts
- [x] T029 [US1] Create TanStack Query hooks (usePromptList, usePromptDetail, useCreatePrompt, useUpdatePrompt, useDeletePrompt) with cache invalidation in frontend/src/hooks/usePrompts.ts
- [x] T030 [P] [US1] Create PromptList presentational component with prompt cards showing title, category badge, description, and timestamps in frontend/src/components/prompts/PromptList.tsx
- [x] T031 [P] [US2] Create CategoryFilter component for orchestrator/task_execution toggle filtering in frontend/src/components/prompts/CategoryFilter.tsx
- [x] T032 [US1] Create PromptsPage container wiring PromptList, CategoryFilter, search input, and pagination in frontend/src/pages/PromptsPage.tsx
- [x] T033 [US1] Create PromptForm component for create and edit modes with title, description, content, category fields and validation in frontend/src/components/prompts/PromptForm.tsx
- [x] T034 [US1] Create CreatePromptPage container using PromptForm and useCreatePrompt hook in frontend/src/pages/CreatePromptPage.tsx
- [x] T035 [US1] Create PromptDetail presentational component displaying full prompt metadata and current version content in frontend/src/components/prompts/PromptDetail.tsx
- [x] T036 [US1] Create PromptDetailPage container with prompt detail, edit/delete actions in frontend/src/pages/PromptDetailPage.tsx
- [x] T037 [US1] Create EditPromptPage container using PromptForm in edit mode with useUpdatePrompt hook and lock_version handling in frontend/src/pages/EditPromptPage.tsx

**Checkpoint**: Prompt CRUD with categories is fully functional. Users can create, view, edit, delete, filter, and search prompts.

---

## Phase 4: User Story 6 — Pre-Populated Mock Data (Priority: P1)

**Goal**: System starts with 10+ realistic sample prompts across both categories with multiple versions, enabling immediate exploration without manual data entry.

**Independent Test**: Start with a fresh database, run `python -m app.seed.data`, verify 10+ prompts appear in the list with at least 2 versions each.

### Implementation

- [x] T038 [US6] Define seed data with 10+ realistic AI agent prompts (5+ orchestrator, 5+ task execution) with meaningful titles, descriptions, and content in backend/app/seed/data.py
- [x] T039 [US6] Implement seed data loader that creates prompts with multiple versions per prompt and CLI entry point (`python -m app.seed.data`) in backend/app/seed/data.py

**Checkpoint**: Database can be populated with realistic sample data via CLI command.

---

## Phase 5: User Story 3 — Version Control for Prompts (Priority: P2)

**Goal**: Users can view the full version history of any prompt, inspect the content of any previous version, and restore a previous version by creating a new version with the restored content (non-destructive).

**Independent Test**: Edit a prompt 3 times, view version history (should show versions 1-4), inspect version 2 content, restore version 2 (should create version 5 with version 2's content).

### Backend Implementation

- [x] T040 [US3] Add version listing (ordered by version_number DESC) and single version retrieval methods to PromptRepository in backend/app/repositories/prompt_repo.py
- [x] T041 [US3] Add version history retrieval and non-destructive version restore logic (creates new version from old content) to PromptService in backend/app/services/prompt_service.py
- [x] T042 [US3] Add version management endpoints (GET /api/prompts/{id}/versions, GET /api/prompts/{id}/versions/{num}, POST /api/prompts/{id}/versions/{num}/restore) to backend/app/api/prompts.py

### Frontend Implementation

- [x] T043 [US3] Add version hooks (usePromptVersions, usePromptVersion, useRestoreVersion) with cache invalidation to frontend/src/hooks/usePrompts.ts
- [x] T044 [US3] Create PromptVersionHistory component with chronological version list, timestamps, change summaries, and restore button in frontend/src/components/prompts/PromptVersionHistory.tsx
- [x] T045 [US3] Integrate version history display and restore functionality into PromptDetailPage in frontend/src/pages/PromptDetailPage.tsx

**Checkpoint**: Full version control is functional. Users can browse history, inspect any version, and restore previous content.

---

## Phase 6: User Story 4 — Automated Prompt Evaluation (Priority: P2)

**Goal**: Users can trigger an automated quality evaluation of any prompt's current version against 6 best-practice criteria (clarity, specificity, structure, context-setting, output format guidance, constraint definition), receiving structured feedback with per-criterion scores and improvement suggestions.

**Independent Test**: Trigger an evaluation on a prompt, verify it returns scores for all 6 criteria (0-100 each), verify overall score is the mean, and check that criteria scoring below 80 include improvement suggestions.

### Backend Implementation

- [x] T046 [P] [US4] Create Evaluation and EvaluationCriterion SQLModel entities with relationships and status lifecycle in backend/app/models/evaluation.py
- [x] T047 [US4] Create Pydantic schemas for evaluations (EvaluationResponse, EvaluationSummary, CriterionResponse, DashboardResponse, CategoryDashboard) in backend/app/schemas/evaluation.py
- [x] T048 [US4] Generate Alembic migration for evaluations and evaluation_criteria tables with indexes and unique constraint (evaluation_id, criterion_name)
- [x] T049 [P] [US4] Create LLM provider Protocol abstraction with concrete implementations for Anthropic, OpenAI, and Google Gemini in backend/app/agents/provider.py
- [x] T050 [P] [US4] Define 6 evaluation criteria as dataclasses with name, description, scoring rubric, and prompt template in backend/app/agents/criteria.py
- [x] T051 [US4] Implement LangGraph fan-out/fan-in evaluation agent using StateGraph with Send API for parallel criterion evaluation and aggregation node in backend/app/agents/evaluator.py
- [x] T052 [US4] Implement EvaluationRepository for evaluation and criteria CRUD operations in backend/app/repositories/evaluation_repo.py
- [x] T053 [US4] Implement EvaluationService for evaluation orchestration (trigger via agent, persist results, handle failures, retrieve by ID) in backend/app/services/evaluation_service.py
- [x] T054 [US4] Implement evaluation API endpoints (POST /api/prompts/{id}/evaluate, GET /api/evaluations/{id}) in backend/app/api/evaluations.py

### Frontend Implementation

- [x] T055 [P] [US4] Create TypeScript interfaces for Evaluation, EvaluationCriterion, EvaluationSummary, and EvaluationStatus in frontend/src/types/evaluation.ts
- [x] T056 [US4] Create evaluation API service functions (triggerEvaluation, getEvaluation) in frontend/src/services/evaluationService.ts
- [x] T057 [US4] Create TanStack Query hooks (useEvaluationDetail, useTriggerEvaluation) with cache invalidation in frontend/src/hooks/useEvaluations.ts
- [x] T058 [P] [US4] Create CriterionScore presentational component displaying criterion name, score bar, and feedback in frontend/src/components/evaluations/CriterionScore.tsx
- [x] T059 [P] [US4] Create ImprovementSuggestions presentational component listing actionable suggestions for low-scoring criteria in frontend/src/components/evaluations/ImprovementSuggestions.tsx
- [x] T060 [US4] Create EvaluationReport component combining overall score, per-criterion scores, and improvement suggestions in frontend/src/components/evaluations/EvaluationReport.tsx
- [x] T061 [US4] Integrate evaluation trigger button and report display into PromptDetailPage in frontend/src/pages/PromptDetailPage.tsx

**Checkpoint**: Automated evaluation is fully functional. Users can evaluate prompts and view detailed feedback reports.

---

## Phase 7: User Story 5 — View Evaluation Results by Category (Priority: P3)

**Goal**: Users can view aggregated evaluation results on a dashboard, filtered by prompt category, with average scores per criterion and the most common improvement points per category.

**Independent Test**: Evaluate multiple prompts across both categories, navigate to dashboard, verify aggregated scores by category, filter to one category, verify criteria breakdown and common improvement patterns.

### Backend Implementation

- [x] T062 [US5] Add dashboard aggregation queries (average scores by category, per-criterion breakdown, common improvements where score < 80) to EvaluationRepository in backend/app/repositories/evaluation_repo.py
- [x] T063 [US5] Add dashboard service logic with optional category filtering to EvaluationService in backend/app/services/evaluation_service.py
- [x] T064 [US5] Implement dashboard API endpoint (GET /api/evaluations/dashboard with optional category filter) in backend/app/api/evaluations.py

### Frontend Implementation

- [x] T065 [US5] Add dashboard hook (useEvaluationDashboard with optional category parameter) to frontend/src/hooks/useEvaluations.ts
- [x] T066 [US5] Create EvaluationDashboard component with category cards, criteria breakdown charts, and common improvement lists in frontend/src/components/evaluations/EvaluationDashboard.tsx
- [x] T067 [US5] Create DashboardPage container with category filter and EvaluationDashboard in frontend/src/pages/DashboardPage.tsx

**Checkpoint**: Evaluation dashboard is functional. Users can analyze quality patterns across prompt categories.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, seed data enrichment, and end-to-end validation

- [x] T068 [P] Extend seed data loader to include pre-run evaluation results on select prompts for dashboard demonstration in backend/app/seed/data.py
- [x] T069 [P] Configure Vite dev server API proxy to backend in frontend/vite.config.ts
- [x] T070 Validate complete quickstart.md flow end-to-end (backend setup, migration, seed, frontend setup, all 6 user stories functional)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──→ Phase 2 (Foundational) ──→ Phase 3 (US1+US2) ──┬──→ Phase 4 (US6)
                                                                     ├──→ Phase 5 (US3)
                                                                     └──→ Phase 6 (US4) ──→ Phase 7 (US5)
                                                                                                   │
                                                                     All ◄─────────────────────────┘
                                                                      └──→ Phase 8 (Polish)
```

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1+US2 (Phase 3)**: Depends on Foundational — MVP delivery milestone
- **US6 (Phase 4)**: Depends on Phase 3 (needs Prompt models and services)
- **US3 (Phase 5)**: Depends on Phase 3 (extends prompt endpoints and UI)
- **US4 (Phase 6)**: Depends on Phase 3 (needs prompts to evaluate); independent of US3 and US6
- **US5 (Phase 7)**: Depends on Phase 6 (needs evaluation data for aggregation)
- **Polish (Phase 8)**: Depends on all previous phases

### Parallel Opportunities After Phase 3

Once US1+US2 completes, three streams can run in parallel:

| Stream A | Stream B | Stream C |
|----------|----------|----------|
| US6 (Seed Data) | US3 (Version Control) | US4 (Evaluation) |
| T038-T039 | T040-T045 | T046-T061 |
| Then: idle | Then: idle | Then: US5 (T062-T067) |

### Within Each User Story

1. Backend: Models → Schemas → Migration → Repository → Service → API endpoints
2. Frontend: Types → API service → Hooks → Presentational components → Container pages
3. Backend endpoints should be functional before starting corresponding frontend work

---

## Parallel Examples

### Phase 2: Foundational

```
# Backend parallel group:
Task: T007 [P] Structured logging in backend/app/core/logging.py
Task: T011 [P] Health endpoint in backend/app/api/health.py

# Frontend parallel group (all independent files):
Task: T013 [P] TanStack Query client in frontend/src/lib/queryClient.ts
Task: T014 [P] API client in frontend/src/services/api.ts
Task: T015 [P] Query key factories in frontend/src/lib/queryKeys.ts
Task: T017 [P] Layout component in frontend/src/components/shared/Layout.tsx
Task: T018 [P] ErrorBoundary in frontend/src/components/shared/ErrorBoundary.tsx
Task: T019 [P] LoadingSpinner in frontend/src/components/shared/LoadingSpinner.tsx
```

### Phase 3: US1+US2

```
# Independent starting tasks:
Task: T020 [P] Enums in backend/app/models/enums.py
Task: T027 [P] TypeScript interfaces in frontend/src/types/prompt.ts

# Frontend parallel components (after hooks are done):
Task: T030 [P] PromptList in frontend/src/components/prompts/PromptList.tsx
Task: T031 [P] CategoryFilter in frontend/src/components/prompts/CategoryFilter.tsx
```

### Phases 5+6: US3 and US4 in Parallel

```
# Developer A: US3 (Version Control)
T040 → T041 → T042 → T043 → T044 → T045

# Developer B: US4 (Evaluation) — simultaneously
T046+T049+T050 [P] → T047 → T048 → T051 → T052 → T053 → T054 → T055 [P] → T056 → T057 → T058+T059 [P] → T060 → T061
```

---

## Implementation Strategy

### MVP First (Phases 1-3: US1+US2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US1+US2 (Prompt CRUD + Categories)
4. **STOP and VALIDATE**: Full CRUD with category filtering works end-to-end
5. Deploy/demo the MVP — users can manage and organize prompts

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1+US2 → Prompt CRUD + Categories → **MVP!**
3. US6 → Seed data → Demo-ready with sample content
4. US3 → Version control → Full prompt management
5. US4 → Automated evaluation → Core differentiator
6. US5 → Dashboard → Analytics capability
7. Polish → Production readiness

### Suggested MVP Scope

**Phase 1 + Phase 2 + Phase 3 (US1+US2)** — delivers a functional prompt repository with category-based organization. Add Phase 4 (US6) for a demo-ready MVP with sample data.

---

## Summary

| Metric | Value |
|--------|-------|
| **Total tasks** | 70 |
| **Setup + Foundational** | 19 tasks (Phases 1-2) |
| **US1+US2 (P1)** | 18 tasks (Phase 3) |
| **US6 (P1)** | 2 tasks (Phase 4) |
| **US3 (P2)** | 6 tasks (Phase 5) |
| **US4 (P2)** | 16 tasks (Phase 6) |
| **US5 (P3)** | 6 tasks (Phase 7) |
| **Polish** | 3 tasks (Phase 8) |
| **Parallel opportunities** | 22 tasks marked [P] |
| **Format validation** | All 70 tasks follow checklist format (checkbox, ID, labels, file paths) |

## Notes

- All tasks use checkbox format: `- [ ] [ID] [P?] [Story?] Description with file path`
- [P] tasks work on different files with no dependencies on incomplete tasks
- [Story] labels map to user stories from spec.md for traceability
- Tests not included — add test tasks if TDD approach is desired
- Commit after each task or logical group for safe progress tracking
- Stop at any checkpoint to validate the story independently
