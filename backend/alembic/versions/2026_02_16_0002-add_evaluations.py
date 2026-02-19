"""add evaluations

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "evaluations",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("prompt_version_id", sa.Uuid(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["prompt_version_id"], ["prompt_versions.id"]),
    )
    op.create_index("ix_evaluations_prompt_version_id", "evaluations", ["prompt_version_id"])
    op.create_index("ix_evaluations_status", "evaluations", ["status"])

    op.create_table(
        "evaluation_criteria",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("evaluation_id", sa.Uuid(), nullable=False),
        sa.Column("criterion_name", sa.String(50), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("feedback", sa.String(), nullable=False),
        sa.Column("improvement_suggestion", sa.String(), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"]),
        sa.UniqueConstraint("evaluation_id", "criterion_name", name="uq_evaluation_criterion"),
    )
    op.create_index(
        "ix_evaluation_criteria_evaluation_id", "evaluation_criteria", ["evaluation_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_evaluation_criteria_evaluation_id", table_name="evaluation_criteria")
    op.drop_table("evaluation_criteria")
    op.drop_index("ix_evaluations_status", table_name="evaluations")
    op.drop_index("ix_evaluations_prompt_version_id", table_name="evaluations")
    op.drop_table("evaluations")
