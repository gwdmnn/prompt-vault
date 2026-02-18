import uuid

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.enums import PromptCategory
from app.models.prompt import Prompt, PromptVersion


class PromptRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, prompt: Prompt) -> Prompt:
        self.session.add(prompt)
        self.session.flush()
        return prompt

    def get_by_id(self, prompt_id: uuid.UUID, active_only: bool = True) -> Prompt | None:
        stmt = select(Prompt).where(Prompt.id == prompt_id)
        if active_only:
            stmt = stmt.where(Prompt.is_active == True)  # noqa: E712
        return self.session.exec(stmt).first()

    def list(
        self,
        category: PromptCategory | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Prompt], int]:
        stmt = select(Prompt).where(Prompt.is_active == True)  # noqa: E712

        if category:
            stmt = stmt.where(Prompt.category == category)

        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                Prompt.title.ilike(pattern)  # type: ignore[union-attr]
                | Prompt.description.ilike(pattern)  # type: ignore[union-attr]
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.exec(count_stmt).one()

        # Paginate
        stmt = stmt.order_by(Prompt.updated_at.desc())  # type: ignore[union-attr]
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        items = list(self.session.exec(stmt).all())

        return items, total

    def update(self, prompt: Prompt) -> Prompt:
        self.session.add(prompt)
        self.session.flush()
        return prompt

    def soft_delete(self, prompt: Prompt) -> None:
        prompt.is_active = False
        self.session.add(prompt)
        self.session.flush()

    # ── Version operations ────────────────────────────────────────

    def create_version(self, version: PromptVersion) -> PromptVersion:
        self.session.add(version)
        self.session.flush()
        return version

    def get_next_version_number(self, prompt_id: uuid.UUID) -> int:
        stmt = select(func.coalesce(func.max(PromptVersion.version_number), 0)).where(
            PromptVersion.prompt_id == prompt_id
        )
        current_max = self.session.exec(stmt).one()
        return current_max + 1

    def get_version_count(self, prompt_id: uuid.UUID) -> int:
        stmt = select(func.count()).where(PromptVersion.prompt_id == prompt_id)
        return self.session.exec(stmt).one()

    def list_versions(self, prompt_id: uuid.UUID) -> list[PromptVersion]:
        stmt = (
            select(PromptVersion)
            .where(PromptVersion.prompt_id == prompt_id)
            .order_by(PromptVersion.version_number.desc())  # type: ignore[union-attr]
        )
        return list(self.session.exec(stmt).all())

    def get_version_by_number(
        self, prompt_id: uuid.UUID, version_number: int
    ) -> PromptVersion | None:
        stmt = select(PromptVersion).where(
            PromptVersion.prompt_id == prompt_id,
            PromptVersion.version_number == version_number,
        )
        return self.session.exec(stmt).first()
