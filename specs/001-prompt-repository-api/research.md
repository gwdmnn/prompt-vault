# Research: Prompt Repository API & UI

**Phase**: 0 — Outline & Research
**Date**: 2026-02-14
**Status**: Complete

## Research Topic 1: LangGraph Evaluation Agent Architecture

### Decision
Use a **fan-out/fan-in StateGraph** with the `Send` API to evaluate all 6 criteria in parallel, followed by an aggregation node.

### Rationale
- **Latency**: Parallel execution of 6 LLM calls completes in ~1 call duration vs ~6x sequential. Meets SC-004 (60s budget) with margin.
- **Scalability**: `Send` API allows adding criteria post-MVP without changing graph topology.
- **Error isolation**: One criterion failure does not block others; partial results are still useful.

### Architecture

```
START -> prepare_evaluation
              |
     (Send API: one per criterion)
     +--------+--------+--------+--------+--------+--------+
     v        v        v        v        v        v        v
  clarity  specificity structure context  format  constraint
     |        |        |        |        |        |        |
     +--------+--------+--------+--------+--------+--------+
              |
         aggregate_results
              |
            END
```

### Key Design Decisions

1. **State schema**: Use `TypedDict` with an `Annotated[list[CriterionResult], operator.add]` reducer to merge parallel criterion results.
2. **Graph construction**: Single `evaluate_criterion` node reused for all criteria via `Send`, with `_current_criterion` field to parametrize behavior.
3. **LLM provider abstraction**: Python `Protocol` class (`LLMProvider`) with `evaluate_criterion` method. Concrete implementations for Anthropic, OpenAI, and Google Gemini. Injected via dependency injection at graph construction time. Satisfies constitution Principle I (Liskov Substitution, Dependency Inversion).
4. **Criteria definitions**: Each criterion defined as a dataclass in `agents/criteria.py` with `name`, `description`, `scoring_rubric`, and `prompt_template`. Open/Closed: new criteria added by creating new instances, not modifying evaluator code.
5. **Error handling**: Each criterion node catches LLM exceptions and returns a `CriterionResult` with `score=0` and error feedback. The aggregation node sets status to `"completed"` even with partial failures, or `"failed"` if all criteria fail.

### Testing Strategy
- Mock the `LLMProvider` protocol with deterministic responses.
- Test graph state transitions: prepare -> fan-out -> evaluate -> aggregate.
- Verify that partial criterion failures produce valid partial reports.
- Use `pytest-asyncio` for async graph invocation.

### Alternatives Considered
- **Sequential chain**: Simpler but 6x latency. Rejected due to SC-004 budget risk.
- **Static parallel edges (6 separate node functions)**: Works but requires code duplication. `Send` API is cleaner.
- **LangChain RunnableParallel**: Less control over state management and error handling than LangGraph StateGraph.

---

## Research Topic 2: Entity Versioning with SQLModel + PostgreSQL

### Decision
Use a **dual FK pattern** with application-level version numbering and `post_update=True` for circular reference handling.

### Rationale
- The `Prompt` table has a `current_version_id` FK pointing to `PromptVersion` for O(1) access to latest content.
- The `PromptVersion` table has a `prompt_id` FK pointing to `Prompt` for the one-to-many history relationship.
- `post_update=True` on the current_version relationship breaks the circular INSERT dependency (SQLAlchemy inserts Prompt first with NULL current_version_id, then inserts PromptVersion, then UPDATEs the pointer).

### Version Numbering
- **Application-level**: `SELECT COALESCE(MAX(version_number), 0) + 1` within the same transaction.
- **Safety net**: `UNIQUE(prompt_id, version_number)` constraint prevents race conditions. If two concurrent transactions compute the same next version, the second commit fails with IntegrityError and can retry.
- **Not triggers**: Triggers hide logic, cannot access user-provided `change_summary`, and complicate testing.

### Soft Delete
- `is_active` boolean field with index on the `Prompt` table.
- Repository layer filters `WHERE is_active = TRUE` by default.
- Deleted prompts retained for data integrity (evaluation history preservation).

### Alternatives Considered
- **Database triggers for versioning**: Rejected — cannot capture `change_summary` from user intent, harder to test without live PostgreSQL.
- **Single table with JSONB history**: Rejected — poor queryability for version history and aggregation.
- **Global auto-increment sequence**: Rejected — version numbers must be per-prompt (1, 2, 3 for each prompt independently).

---

## Research Topic 3: Optimistic Concurrency Control

### Decision
Use an integer `lock_version` column with SQLAlchemy's built-in `version_id_col` mapper argument.

### Rationale
- SQLAlchemy automatically adds `WHERE lock_version = <expected>` to every UPDATE and increments it. Zero manual SQL needed.
- Avoids datetime precision issues (microsecond round-tripping through JSON serialization).
- Raises `StaleDataError` on conflict, which the service layer maps to HTTP 409.
- Client must echo `lock_version` on every update request.

### API Contract
The `PromptUpdate` schema includes a required `lock_version: int` field. The client reads a prompt (gets `lock_version: 3`), makes edits, sends PUT with `lock_version: 3`. If another edit occurred (bumping to 4), the update fails with 409 Conflict and a descriptive message.

### Alternatives Considered
- **Timestamp-based (`updated_at` comparison)**: Simpler schema but susceptible to datetime precision mismatches after JSON round-tripping. Rejected.
- **No concurrency control**: Single-user MVP could skip this, but the spec explicitly mentions concurrent edit detection. Included for correctness.

---

## Research Topic 4: Frontend State Management

### Decision
Use **TanStack Query v5** for all server state. No additional state manager (Redux, Zustand) needed for MVP.

### Rationale
- TanStack Query handles caching, background refetching, optimistic updates, and cache invalidation out of the box.
- The application is primarily server-state driven (prompts, versions, evaluations). Minimal client-only state exists (form inputs, UI toggles handled by React's `useState`).
- Avoids unnecessary complexity. Constitution Principle II allows context/state manager "only when prop drilling exceeds 3 levels" — TanStack Query eliminates the need.

### Query Key Factory Pattern
Hierarchical key structure enables precise cache invalidation:

```typescript
export const promptKeys = {
  all: ['prompts'] as const,
  lists: () => [...promptKeys.all, 'list'] as const,
  list: (filters: PromptListFilters) => [...promptKeys.lists(), filters] as const,
  details: () => [...promptKeys.all, 'detail'] as const,
  detail: (id: string) => [...promptKeys.details(), id] as const,
  versions: (id: string) => [...promptKeys.detail(id), 'versions'] as const,
};

export const evaluationKeys = {
  all: ['evaluations'] as const,
  lists: () => [...evaluationKeys.all, 'list'] as const,
  list: (filters: EvalListFilters) => [...evaluationKeys.lists(), filters] as const,
  detail: (id: string) => [...evaluationKeys.all, 'detail', id] as const,
  dashboard: () => [...evaluationKeys.all, 'dashboard'] as const,
  dashboardByCategory: (cat: PromptCategory) => [...evaluationKeys.dashboard(), cat] as const,
};
```

### Key v5 Changes
- `cacheTime` renamed to `gcTime`.
- Single object argument for all hooks: `useQuery({ queryKey, queryFn })`.
- `status: 'loading'` renamed to `status: 'pending'`.
- No `onSuccess`/`onError` callbacks on queries — use `useEffect` or mutation callbacks.

### Optimistic Updates
Use `useMutation` with `onMutate` for optimistic cache updates on prompt edit/delete. Roll back via `onError` using the snapshot stored in `onMutate` context.

### Alternatives Considered
- **React Context + useReducer**: Viable but would reimplement what TanStack Query provides (caching, deduplication, background refresh). Rejected.
- **Zustand/Jotai**: Overkill for MVP server-state patterns. Rejected.
- **Redux Toolkit Query**: Heavier API surface, less idiomatic for this use case. Rejected.

---

## Research Topic 5: React Router v7 + Vite 6 Setup

### Decision
Use **React Router v7** in SPA (client-side) mode with `createBrowserRouter`. No SSR/RSC needed for MVP.

### Rationale
- React Router v7 (formerly Remix) supports both framework mode (SSR) and library mode (SPA). For the MVP, library/SPA mode keeps complexity low.
- `createBrowserRouter` provides data loading via `loader` functions, but TanStack Query handles data fetching, so loaders are optional.
- Vite 6+ has built-in React support via `@vitejs/plugin-react`.

### Route Structure

```typescript
const router = createBrowserRouter([
  { path: '/', element: <Layout />, children: [
    { index: true, element: <PromptsPage /> },
    { path: 'prompts/new', element: <CreatePromptPage /> },
    { path: 'prompts/:promptId', element: <PromptDetailPage /> },
    { path: 'prompts/:promptId/edit', element: <EditPromptPage /> },
    { path: 'dashboard', element: <DashboardPage /> },
  ]},
]);
```

### Alternatives Considered
- **React Router v7 framework mode (SSR)**: Unnecessary for single-user MVP. Adds server complexity. Rejected.
- **Next.js**: Overkill for an SPA that talks to a separate FastAPI backend. Rejected.
- **TanStack Router**: Excellent type safety but smaller ecosystem. React Router v7 is the safer choice for the MVP. Could be reconsidered post-MVP.

---

## Research Topic 6: Evaluation Criteria Scoring

### Decision
Use a **0-100 integer scale** per criterion. Overall score is the **unweighted arithmetic mean**. Suggestions are triggered for any criterion below 80.

### Rationale
- Integer scale avoids floating-point display issues in the UI.
- Unweighted mean is simplest and most transparent for MVP. Weighted scoring can be added post-MVP without schema changes.
- The 80 threshold for improvement suggestions matches SC-005 ("at least one specific improvement suggestion per criterion scored below 80%").

### Criteria Definitions

| Criterion | Description | What scores high (80+) | What scores low (<50) |
|-----------|-------------|----------------------|---------------------|
| Clarity | How clear and unambiguous the prompt is | Single interpretation, precise language | Vague, ambiguous, contradictory instructions |
| Specificity | How detailed and specific the instructions are | Concrete parameters, defined scope | Overly broad, missing constraints |
| Structure | How well-organized the prompt is | Logical sections, clear flow | Disorganized, jumbled requirements |
| Context-Setting | How well background context is provided | Role, audience, domain clearly stated | Missing context, assumed knowledge |
| Output Format Guidance | How clearly the expected output is defined | Explicit format, examples provided | No format specified, unclear expectations |
| Constraint Definition | How well constraints and boundaries are defined | Clear limits, edge case handling | No constraints, unbounded scope |

### LLM Prompt Template Pattern
Each criterion's evaluation prompt follows a standard template:
1. System message: "You are a prompt quality evaluator."
2. Criterion description and scoring rubric.
3. The prompt content to evaluate.
4. Structured output format (JSON with `score`, `feedback`, `improvement_suggestions`).
5. Use Pydantic model as the output schema for structured LLM output.

### Alternatives Considered
- **1-10 scale**: Less granularity. Rejected.
- **Letter grades (A-F)**: Harder to aggregate mathematically. Rejected.
- **Weighted average**: Adds configuration complexity. Deferred to post-MVP.

---

## Research Topic 7: Database Session & Alembic Configuration

### Decision
Use FastAPI's dependency injection with `yield`-based session generator. Alembic configured with `SQLModel.metadata` and `compare_type=True`.

### Rationale
- `yield`-based sessions ensure proper cleanup (commit on success, rollback on exception).
- `SQLModel.metadata` as `target_metadata` in `alembic/env.py` ensures all table models are discovered by autogenerate.
- `compare_type=True` detects column type changes that Alembic would otherwise miss.

### Critical Setup Notes
1. All SQLModel table models must be imported in `alembic/env.py` before autogenerate runs.
2. Keep Pydantic-only schemas in `app/schemas/` (separate from `app/models/`) to avoid confusing Alembic metadata detection.
3. The circular FK between `prompts.current_version_id` and `prompt_versions.prompt_id` may require `DEFERRABLE INITIALLY DEFERRED` constraint or a two-step migration (create tables first, add FK later).
4. Use timestamp-based migration file naming: `%%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(slug)s`.
5. Connection pool: `pool_pre_ping=True`, `pool_size=5`, `max_overflow=10` for MVP scale.

---

## Summary of All Decisions

| Topic | Decision | Key Rationale |
|-------|----------|---------------|
| Evaluation agent | Fan-out/fan-in StateGraph with Send API | Parallel execution meets 60s budget |
| State schema | TypedDict with operator.add reducer | Type-safe, merge-friendly for parallel results |
| LLM abstraction | Protocol class with DI | Liskov Substitution, testability |
| Entity versioning | Dual FK with post_update=True | O(1) current version access, clean history |
| Version numbering | Application-level MAX+1 with UNIQUE constraint | Per-prompt numbering, race condition safety |
| Concurrency control | lock_version integer with version_id_col | Automatic, no precision issues |
| Soft delete | is_active boolean with index | Simple, preserves evaluation history |
| Frontend state | TanStack Query v5, no additional state manager | Server-state driven app, minimal client state |
| Query keys | Hierarchical factory pattern | Precise cache invalidation |
| Routing | React Router v7 SPA mode | Simple, no SSR needed for MVP |
| Scoring | 0-100 integer, unweighted mean, 80 threshold | Transparent, matches SC-005 |
| DB sessions | Yield-based DI with FastAPI Depends | Proper cleanup, testable |
| Migrations | Alembic with SQLModel.metadata, compare_type=True | Reliable autogeneration |
