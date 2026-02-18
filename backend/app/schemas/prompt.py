import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import PromptCategory


# ── Request schemas ──────────────────────────────────────────────

class PromptCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    content: str = Field(min_length=1, max_length=50000)
    category: PromptCategory


class PromptUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    content: str | None = Field(default=None, min_length=1, max_length=50000)
    category: PromptCategory | None = None
    change_summary: str = Field(default="", max_length=500)
    lock_version: int


# ── Response schemas ─────────────────────────────────────────────

class PromptVersionResponse(BaseModel):
    id: uuid.UUID
    prompt_id: uuid.UUID
    version_number: int
    content: str
    change_summary: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluationSummaryInPrompt(BaseModel):
    id: uuid.UUID
    overall_score: float | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PromptResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    category: PromptCategory
    is_active: bool
    lock_version: int
    created_at: datetime
    updated_at: datetime
    version_count: int

    model_config = {"from_attributes": True}


class PromptDetailResponse(PromptResponse):
    current_version: PromptVersionResponse
    latest_evaluation: EvaluationSummaryInPrompt | None = None


class PromptListResponse(BaseModel):
    items: list[PromptResponse]
    total: int
    page: int
    page_size: int
