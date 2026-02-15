# Data Model: Prompt Repository API & UI

**Phase**: 1 — Design & Contracts
**Date**: 2026-02-14
**Status**: Complete

## Entity Relationship Diagram

```
┌─────────────────────────┐       ┌─────────────────────────────┐
│        Prompt            │       │      PromptVersion          │
├─────────────────────────┤       ├─────────────────────────────┤
│ id: UUID (PK)           │──1:N──│ id: UUID (PK)               │
│ title: VARCHAR(200)     │       │ prompt_id: UUID (FK)         │
│ description: VARCHAR(2K)│       │ version_number: INT          │
│ category: ENUM          │──1:1──│ content: VARCHAR(50K)        │
│ is_active: BOOLEAN      │  ▲    │ change_summary: VARCHAR(500) │
│ lock_version: INT       │  │    │ created_at: TIMESTAMP        │
│ created_at: TIMESTAMP   │  │    └─────────────────────────────┘
│ updated_at: TIMESTAMP   │  │              │
│ current_version_id: UUID│──┘              │
└─────────────────────────┘                 │
                                            │ 1:N (via prompt_version_id)
                                            ▼
┌─────────────────────────┐       ┌─────────────────────────────┐
│      Evaluation          │       │   EvaluationCriterion       │
├─────────────────────────┤       ├─────────────────────────────┤
│ id: UUID (PK)           │──1:N──│ id: UUID (PK)               │
│ prompt_version_id: UUID  │       │ evaluation_id: UUID (FK)    │
│ overall_score: FLOAT    │       │ criterion_name: VARCHAR(50)  │
│ status: ENUM            │       │ score: INT                   │
│ error_message: TEXT     │       │ feedback: TEXT                │
│ created_at: TIMESTAMP   │       │ improvement_suggestion: TEXT  │
└─────────────────────────┘       └─────────────────────────────┘
```

## Entities

### Prompt

Represents a reusable prompt template with metadata. The `current_version_id` provides O(1) access to the latest version content.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, default `gen_random_uuid()` | Unique identifier |
| `title` | VARCHAR(200) | NOT NULL, indexed | Prompt display title |
| `description` | VARCHAR(2000) | NOT NULL, default `''` | Brief description of the prompt's purpose |
| `category` | ENUM(`orchestrator`, `task_execution`) | NOT NULL, indexed | Prompt category per FR-006 |
| `is_active` | BOOLEAN | NOT NULL, default `TRUE`, indexed | Soft delete flag per FR-005 |
| `lock_version` | INTEGER | NOT NULL, default `1` | Optimistic concurrency token |
| `created_at` | TIMESTAMP | NOT NULL, default `now()` | Record creation time |
| `updated_at` | TIMESTAMP | NOT NULL, default `now()` | Last modification time |
| `current_version_id` | UUID | FK -> `prompt_versions.id`, NULLABLE | Points to latest version (NULL only during initial insert, immediately updated) |

**Indexes**:
- `ix_prompts_title` on `title`
- `ix_prompts_category` on `category`
- `ix_prompts_is_active` on `is_active`

**Relationships**:
- `current_version` -> `PromptVersion` (many-to-one via `current_version_id`, `post_update=True`)
- `versions` -> `PromptVersion[]` (one-to-many via `PromptVersion.prompt_id`, ordered by `version_number DESC`)

---

### PromptVersion

Represents an immutable content snapshot of a prompt at a specific version. Created on every edit per FR-004.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, default `gen_random_uuid()` | Unique identifier |
| `prompt_id` | UUID | FK -> `prompts.id`, NOT NULL, indexed | Parent prompt reference |
| `version_number` | INTEGER | NOT NULL, >= 1 | Per-prompt sequential version (auto-calculated) |
| `content` | VARCHAR(50000) | NOT NULL | Prompt content body per FR-018 |
| `change_summary` | VARCHAR(500) | NOT NULL, default `''` | User-provided description of changes |
| `created_at` | TIMESTAMP | NOT NULL, default `now()` | Version creation time |

**Constraints**:
- `uq_prompt_version_number` UNIQUE(`prompt_id`, `version_number`) — prevents race conditions in concurrent version creation

**Indexes**:
- `ix_prompt_versions_prompt_id` on `prompt_id`

**Relationships**:
- `prompt` -> `Prompt` (many-to-one via `prompt_id`)

---

### Evaluation

Represents an automated quality assessment of a specific prompt version per FR-010, FR-013.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, default `gen_random_uuid()` | Unique identifier |
| `prompt_version_id` | UUID | FK -> `prompt_versions.id`, NOT NULL, indexed | The specific version evaluated |
| `overall_score` | FLOAT | NULLABLE | Weighted average of criterion scores (NULL while pending) |
| `status` | ENUM(`pending`, `completed`, `failed`) | NOT NULL, default `'pending'` | Evaluation lifecycle state |
| `error_message` | TEXT | NULLABLE | Error description when status is `failed` |
| `created_at` | TIMESTAMP | NOT NULL, default `now()` | Evaluation start time |
| `completed_at` | TIMESTAMP | NULLABLE | Evaluation completion time |

**Indexes**:
- `ix_evaluations_prompt_version_id` on `prompt_version_id`
- `ix_evaluations_status` on `status`

**Relationships**:
- `prompt_version` -> `PromptVersion` (many-to-one via `prompt_version_id`)
- `criteria` -> `EvaluationCriterion[]` (one-to-many via `EvaluationCriterion.evaluation_id`)

---

### EvaluationCriterion

Represents a single evaluation dimension with its score and feedback per FR-011, FR-012.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, default `gen_random_uuid()` | Unique identifier |
| `evaluation_id` | UUID | FK -> `evaluations.id`, NOT NULL, indexed | Parent evaluation |
| `criterion_name` | VARCHAR(50) | NOT NULL | One of: `clarity`, `specificity`, `structure`, `context_setting`, `output_format_guidance`, `constraint_definition` |
| `score` | INTEGER | NOT NULL, 0-100 | Criterion score |
| `feedback` | TEXT | NOT NULL | Detailed feedback text |
| `improvement_suggestion` | TEXT | NOT NULL, default `''` | Actionable improvement suggestion (required when score < 80 per SC-005) |

**Constraints**:
- `uq_evaluation_criterion` UNIQUE(`evaluation_id`, `criterion_name`) — one score per criterion per evaluation

**Indexes**:
- `ix_evaluation_criteria_evaluation_id` on `evaluation_id`

**Relationships**:
- `evaluation` -> `Evaluation` (many-to-one via `evaluation_id`)

---

## Enumerations

### PromptCategory

```python
class PromptCategory(str, Enum):
    ORCHESTRATOR = "orchestrator"
    TASK_EXECUTION = "task_execution"
```

- `orchestrator` — Prompts that coordinate multi-step workflows
- `task_execution` — Prompts that perform a specific task

### EvaluationStatus

```python
class EvaluationStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## Validation Rules

| Entity | Field | Rule | Error Message |
|--------|-------|------|---------------|
| Prompt | `title` | 1-200 characters, non-empty | "Title must be between 1 and 200 characters" |
| Prompt | `description` | 0-2000 characters | "Description must not exceed 2000 characters" |
| Prompt | `category` | Must be valid PromptCategory value | "Category must be 'orchestrator' or 'task_execution'" |
| PromptVersion | `content` | 1-50,000 characters, non-empty | "Content must be between 1 and 50,000 characters" (FR-018) |
| PromptVersion | `change_summary` | 0-500 characters | "Change summary must not exceed 500 characters" |
| EvaluationCriterion | `score` | Integer 0-100 | "Score must be between 0 and 100" |
| EvaluationCriterion | `criterion_name` | Must be one of 6 predefined criteria | "Invalid criterion name" |

---

## State Transitions

### Prompt Lifecycle

```
Created (is_active=TRUE)
    │
    ├── Edit metadata → Updated (new updated_at, lock_version++)
    ├── Edit content  → Updated + New PromptVersion created
    ├── Delete        → Soft-deleted (is_active=FALSE)
    └── Evaluate      → Evaluation created for current_version
```

### Evaluation Lifecycle

```
Triggered (status=PENDING)
    │
    ├── Success → COMPLETED (overall_score set, criteria populated)
    └── Failure → FAILED (error_message set)
```

### Version Lifecycle

```
Created (immutable)
    │
    ├── Referenced as current_version → Active display
    ├── Superseded by newer version  → Historical (still accessible via FR-008)
    └── Restored (FR-009)            → New version created with restored content
```

---

## Aggregation Queries (Dashboard Support)

### Average Scores by Category (FR-014)

```sql
SELECT p.category,
       AVG(e.overall_score) as avg_score,
       COUNT(e.id) as evaluation_count
FROM evaluations e
JOIN prompt_versions pv ON e.prompt_version_id = pv.id
JOIN prompts p ON pv.prompt_id = p.id
WHERE e.status = 'completed' AND p.is_active = TRUE
GROUP BY p.category;
```

### Most Common Improvement Points by Category (FR-015)

```sql
SELECT p.category,
       ec.criterion_name,
       COUNT(*) as low_score_count,
       AVG(ec.score) as avg_criterion_score
FROM evaluation_criteria ec
JOIN evaluations e ON ec.evaluation_id = e.id
JOIN prompt_versions pv ON e.prompt_version_id = pv.id
JOIN prompts p ON pv.prompt_id = p.id
WHERE ec.score < 80 AND e.status = 'completed' AND p.is_active = TRUE
GROUP BY p.category, ec.criterion_name
ORDER BY p.category, low_score_count DESC;
```

### Prompt Search (FR-017)

```sql
SELECT p.*, pv.content
FROM prompts p
JOIN prompt_versions pv ON p.current_version_id = pv.id
WHERE p.is_active = TRUE
  AND (p.title ILIKE '%{query}%' OR pv.content ILIKE '%{query}%')
ORDER BY p.updated_at DESC;
```

*Note: For MVP, ILIKE is sufficient. Post-MVP, consider PostgreSQL full-text search (`tsvector`/`tsquery`) for better performance on large datasets.*
