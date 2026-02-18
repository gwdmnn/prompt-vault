import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import EvaluationStatus, PromptCategory


# ── Response schemas ─────────────────────────────────────────────

class CriterionResponse(BaseModel):
    criterion_name: str
    score: int
    feedback: str
    improvement_suggestion: str

    model_config = {"from_attributes": True}


class EvaluationSummary(BaseModel):
    id: uuid.UUID
    overall_score: float | None
    status: EvaluationStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluationResponse(BaseModel):
    id: uuid.UUID
    prompt_version_id: uuid.UUID
    overall_score: float | None
    status: EvaluationStatus
    error_message: str | None = None
    criteria: list[CriterionResponse]
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Dashboard schemas ────────────────────────────────────────────

class CriteriaBreakdown(BaseModel):
    criterion_name: str
    avg_score: float


class CommonImprovement(BaseModel):
    criterion_name: str
    occurrence_count: int
    avg_score: float


class CategoryDashboard(BaseModel):
    category: PromptCategory
    avg_score: float
    evaluation_count: int
    criteria_breakdown: list[CriteriaBreakdown]
    common_improvements: list[CommonImprovement]


class DashboardResponse(BaseModel):
    categories: list[CategoryDashboard]
    total_evaluations: int
