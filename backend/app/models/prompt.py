import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Enum, String, event
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import PromptCategory


class Prompt(SQLModel, table=True):
    __tablename__ = "prompts"
    __mapper_args__ = {"version_id_col": "lock_version"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=200, index=True, sa_column_kwargs={"nullable": False})
    description: str = Field(
        default="", max_length=2000, sa_column_kwargs={"nullable": False}
    )
    category: PromptCategory = Field(
        sa_column=Column(Enum(PromptCategory, name="promptcategory"), nullable=False, index=True)
    )
    is_active: bool = Field(default=True, index=True, sa_column_kwargs={"nullable": False})
    lock_version: int = Field(default=1, sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"nullable": False},
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"nullable": False},
    )
    current_version_id: uuid.UUID | None = Field(
        default=None, foreign_key="prompt_versions.id"
    )

    # Relationships
    versions: list["PromptVersion"] = Relationship(
        back_populates="prompt",
        sa_relationship_kwargs={
            "foreign_keys": "PromptVersion.prompt_id",
            "order_by": "PromptVersion.version_number.desc()",
            "lazy": "selectin",
        },
    )
    current_version: "PromptVersion | None" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "Prompt.current_version_id",
            "post_update": True,
            "lazy": "joined",
        },
    )


class PromptVersion(SQLModel, table=True):
    __tablename__ = "prompt_versions"
    __table_args__ = (
        {"comment": "Immutable content snapshots of prompts"},
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    prompt_id: uuid.UUID = Field(foreign_key="prompts.id", index=True, nullable=False)
    version_number: int = Field(ge=1, sa_column_kwargs={"nullable": False})
    content: str = Field(
        max_length=50000,
        sa_column=Column(String(50000), nullable=False),
    )
    change_summary: str = Field(default="", max_length=500, sa_column_kwargs={"nullable": False})
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"nullable": False},
    )

    # Relationships
    prompt: Prompt | None = Relationship(
        back_populates="versions",
        sa_relationship_kwargs={"foreign_keys": "PromptVersion.prompt_id"},
    )
