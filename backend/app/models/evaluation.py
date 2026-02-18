import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Enum, String
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import EvaluationStatus


class Evaluation(SQLModel, table=True):
    __tablename__ = "evaluations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    prompt_version_id: uuid.UUID = Field(
        foreign_key="prompt_versions.id", index=True, nullable=False
    )
    overall_score: float | None = Field(default=None)
    status: EvaluationStatus = Field(
        default=EvaluationStatus.PENDING,
        sa_column=Column(
            Enum(EvaluationStatus, name="evaluationstatus"),
            nullable=False,
            index=True,
            server_default="pending",
        ),
    )
    error_message: str | None = Field(default=None, sa_column=Column(String, nullable=True))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"nullable": False},
    )
    completed_at: datetime | None = Field(default=None)

    # Relationships
    criteria: list["EvaluationCriterion"] = Relationship(
        back_populates="evaluation",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class EvaluationCriterion(SQLModel, table=True):
    __tablename__ = "evaluation_criteria"
    __table_args__ = (
        {"comment": "Individual criterion scores within an evaluation"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    evaluation_id: uuid.UUID = Field(
        foreign_key="evaluations.id", index=True, nullable=False
    )
    criterion_name: str = Field(max_length=50, sa_column_kwargs={"nullable": False})
    score: int = Field(ge=0, le=100, sa_column_kwargs={"nullable": False})
    feedback: str = Field(sa_column=Column(String, nullable=False))
    improvement_suggestion: str = Field(
        default="", sa_column=Column(String, nullable=False, server_default="")
    )

    # Relationships
    evaluation: Evaluation | None = Relationship(back_populates="criteria")
