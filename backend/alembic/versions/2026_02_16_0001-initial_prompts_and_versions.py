"""initial prompts and versions

Revision ID: 0001
Revises:
Create Date: 2026-02-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    promptcategory = sa.Enum("orchestrator", "task_execution", name="promptcategory")
    promptcategory.create(op.get_bind(), checkfirst=True)

    # Create prompts table (without current_version_id FK first)
    op.create_table(
        "prompts",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(2000), nullable=False, server_default=""),
        sa.Column("category", promptcategory, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("lock_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("current_version_id", sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_prompts_title", "prompts", ["title"])
    op.create_index("ix_prompts_category", "prompts", ["category"])
    op.create_index("ix_prompts_is_active", "prompts", ["is_active"])

    # Create prompt_versions table
    op.create_table(
        "prompt_versions",
        sa.Column("id", sa.Uuid(), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("prompt_id", sa.Uuid(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(50000), nullable=False),
        sa.Column("change_summary", sa.String(500), nullable=False, server_default=""),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["prompt_id"], ["prompts.id"]),
        sa.UniqueConstraint("prompt_id", "version_number", name="uq_prompt_version_number"),
    )
    op.create_index("ix_prompt_versions_prompt_id", "prompt_versions", ["prompt_id"])

    # Add FK from prompts.current_version_id to prompt_versions.id (post-create)
    op.create_foreign_key(
        "fk_prompts_current_version_id",
        "prompts",
        "prompt_versions",
        ["current_version_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_prompts_current_version_id", "prompts", type_="foreignkey")
    op.drop_index("ix_prompt_versions_prompt_id", table_name="prompt_versions")
    op.drop_table("prompt_versions")
    op.drop_index("ix_prompts_is_active", table_name="prompts")
    op.drop_index("ix_prompts_category", table_name="prompts")
    op.drop_index("ix_prompts_title", table_name="prompts")
    op.drop_table("prompts")
    sa.Enum(name="promptcategory").drop(op.get_bind(), checkfirst=True)
