import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.deps import get_prompt_service
from app.models.enums import PromptCategory
from app.schemas.prompt import (
    PromptCreate,
    PromptDetailResponse,
    PromptListResponse,
    PromptUpdate,
    PromptVersionResponse,
)
from app.services.prompt_service import PromptService, PromptServiceError

router = APIRouter(tags=["prompts"])


def _error_response(exc: PromptServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc), "code": exc.code},
    )


@router.get("/prompts", response_model=PromptListResponse)
def list_prompts(
    category: PromptCategory | None = None,
    search: str | None = Query(default=None, max_length=200),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: PromptService = Depends(get_prompt_service),
):
    return service.list(category=category, search=search, page=page, page_size=page_size)


@router.post("/prompts", response_model=PromptDetailResponse, status_code=201)
def create_prompt(
    data: PromptCreate,
    service: PromptService = Depends(get_prompt_service),
):
    return service.create(data)


@router.get("/prompts/{prompt_id}", response_model=PromptDetailResponse)
def get_prompt(
    prompt_id: uuid.UUID,
    service: PromptService = Depends(get_prompt_service),
):
    try:
        return service.get(prompt_id)
    except PromptServiceError as exc:
        return _error_response(exc)


@router.put("/prompts/{prompt_id}", response_model=PromptDetailResponse)
def update_prompt(
    prompt_id: uuid.UUID,
    data: PromptUpdate,
    service: PromptService = Depends(get_prompt_service),
):
    try:
        return service.update(prompt_id, data)
    except PromptServiceError as exc:
        return _error_response(exc)


@router.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(
    prompt_id: uuid.UUID,
    service: PromptService = Depends(get_prompt_service),
):
    try:
        service.delete(prompt_id)
    except PromptServiceError as exc:
        return _error_response(exc)


# ── Version endpoints ─────────────────────────────────────────

@router.get("/prompts/{prompt_id}/versions", response_model=list[PromptVersionResponse])
def list_prompt_versions(
    prompt_id: uuid.UUID,
    service: PromptService = Depends(get_prompt_service),
):
    try:
        return service.list_versions(prompt_id)
    except PromptServiceError as exc:
        return _error_response(exc)


@router.get(
    "/prompts/{prompt_id}/versions/{version_number}",
    response_model=PromptVersionResponse,
)
def get_prompt_version(
    prompt_id: uuid.UUID,
    version_number: int,
    service: PromptService = Depends(get_prompt_service),
):
    try:
        return service.get_version(prompt_id, version_number)
    except PromptServiceError as exc:
        return _error_response(exc)


@router.post(
    "/prompts/{prompt_id}/versions/{version_number}/restore",
    response_model=PromptVersionResponse,
    status_code=201,
)
def restore_prompt_version(
    prompt_id: uuid.UUID,
    version_number: int,
    service: PromptService = Depends(get_prompt_service),
):
    try:
        return service.restore_version(prompt_id, version_number)
    except PromptServiceError as exc:
        return _error_response(exc)
