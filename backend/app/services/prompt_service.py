import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm.exc import StaleDataError

from app.models.enums import PromptCategory
from app.models.prompt import Prompt, PromptVersion
from app.repositories.prompt_repo import PromptRepository
from app.schemas.prompt import (
    PromptCreate,
    PromptDetailResponse,
    PromptListResponse,
    PromptResponse,
    PromptUpdate,
    PromptVersionResponse,
)

logger = logging.getLogger(__name__)


class PromptServiceError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class PromptNotFoundError(PromptServiceError):
    def __init__(self, prompt_id: uuid.UUID):
        super().__init__(f"Prompt {prompt_id} not found", "NOT_FOUND", 404)


class PromptConflictError(PromptServiceError):
    def __init__(self, message: str = "Prompt was modified by another request"):
        super().__init__(message, "CONFLICT", 409)


class PromptService:
    def __init__(self, repo: PromptRepository):
        self.repo = repo

    def create(self, data: PromptCreate) -> PromptDetailResponse:
        prompt = Prompt(
            title=data.title,
            description=data.description,
            category=data.category,
        )
        prompt = self.repo.create(prompt)

        version = PromptVersion(
            prompt_id=prompt.id,
            version_number=1,
            content=data.content,
            change_summary="Initial version",
        )
        version = self.repo.create_version(version)

        prompt.current_version_id = version.id
        prompt = self.repo.update(prompt)

        logger.info("Created prompt %s with version 1", prompt.id)
        return self._to_detail_response(prompt, version, 1)

    def get(self, prompt_id: uuid.UUID) -> PromptDetailResponse:
        prompt = self.repo.get_by_id(prompt_id)
        if not prompt:
            raise PromptNotFoundError(prompt_id)

        version_count = self.repo.get_version_count(prompt_id)
        return self._to_detail_response(prompt, prompt.current_version, version_count)

    def list(
        self,
        category: PromptCategory | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PromptListResponse:
        items, total = self.repo.list(category, search, page, page_size)
        return PromptListResponse(
            items=[self._to_response(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def update(self, prompt_id: uuid.UUID, data: PromptUpdate) -> PromptDetailResponse:
        prompt = self.repo.get_by_id(prompt_id)
        if not prompt:
            raise PromptNotFoundError(prompt_id)

        # Optimistic concurrency check
        if prompt.lock_version != data.lock_version:
            raise PromptConflictError()

        # Update metadata
        if data.title is not None:
            prompt.title = data.title
        if data.description is not None:
            prompt.description = data.description
        if data.category is not None:
            prompt.category = data.category

        prompt.updated_at = datetime.now(timezone.utc)

        # Create new version if content changed
        new_version = None
        if data.content is not None and (
            prompt.current_version is None or data.content != prompt.current_version.content
        ):
            next_num = self.repo.get_next_version_number(prompt_id)
            new_version = PromptVersion(
                prompt_id=prompt_id,
                version_number=next_num,
                content=data.content,
                change_summary=data.change_summary,
            )
            new_version = self.repo.create_version(new_version)
            prompt.current_version_id = new_version.id

        try:
            prompt = self.repo.update(prompt)
        except StaleDataError:
            raise PromptConflictError()

        current = new_version or prompt.current_version
        version_count = self.repo.get_version_count(prompt_id)
        logger.info("Updated prompt %s", prompt_id)
        return self._to_detail_response(prompt, current, version_count)

    def delete(self, prompt_id: uuid.UUID) -> None:
        prompt = self.repo.get_by_id(prompt_id)
        if not prompt:
            raise PromptNotFoundError(prompt_id)
        self.repo.soft_delete(prompt)
        logger.info("Soft-deleted prompt %s", prompt_id)

    # ── Version operations ────────────────────────────────────────

    def list_versions(self, prompt_id: uuid.UUID) -> list[PromptVersionResponse]:
        prompt = self.repo.get_by_id(prompt_id)
        if not prompt:
            raise PromptNotFoundError(prompt_id)
        versions = self.repo.list_versions(prompt_id)
        return [PromptVersionResponse.model_validate(v) for v in versions]

    def get_version(self, prompt_id: uuid.UUID, version_number: int) -> PromptVersionResponse:
        prompt = self.repo.get_by_id(prompt_id)
        if not prompt:
            raise PromptNotFoundError(prompt_id)
        version = self.repo.get_version_by_number(prompt_id, version_number)
        if not version:
            raise PromptServiceError(
                f"Version {version_number} not found", "NOT_FOUND", 404
            )
        return PromptVersionResponse.model_validate(version)

    def restore_version(
        self, prompt_id: uuid.UUID, version_number: int
    ) -> PromptVersionResponse:
        prompt = self.repo.get_by_id(prompt_id)
        if not prompt:
            raise PromptNotFoundError(prompt_id)

        old_version = self.repo.get_version_by_number(prompt_id, version_number)
        if not old_version:
            raise PromptServiceError(
                f"Version {version_number} not found", "NOT_FOUND", 404
            )

        next_num = self.repo.get_next_version_number(prompt_id)
        new_version = PromptVersion(
            prompt_id=prompt_id,
            version_number=next_num,
            content=old_version.content,
            change_summary=f"Restored from version {version_number}",
        )
        new_version = self.repo.create_version(new_version)
        prompt.current_version_id = new_version.id
        prompt.updated_at = datetime.now(timezone.utc)
        self.repo.update(prompt)

        logger.info("Restored prompt %s to version %d (new version %d)", prompt_id, version_number, next_num)
        return PromptVersionResponse.model_validate(new_version)

    # ── Response helpers ──────────────────────────────────────────

    def _to_response(self, prompt: Prompt) -> PromptResponse:
        version_count = self.repo.get_version_count(prompt.id)
        return PromptResponse(
            id=prompt.id,
            title=prompt.title,
            description=prompt.description,
            category=prompt.category,
            is_active=prompt.is_active,
            lock_version=prompt.lock_version,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
            version_count=version_count,
        )

    def _to_detail_response(
        self,
        prompt: Prompt,
        current_version: PromptVersion | None,
        version_count: int,
    ) -> PromptDetailResponse:
        cv = PromptVersionResponse.model_validate(current_version) if current_version else None
        return PromptDetailResponse(
            id=prompt.id,
            title=prompt.title,
            description=prompt.description,
            category=prompt.category,
            is_active=prompt.is_active,
            lock_version=prompt.lock_version,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
            version_count=version_count,
            current_version=cv,  # type: ignore[arg-type]
        )
