import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.deps import get_evaluation_service
from app.models.enums import PromptCategory
from app.schemas.evaluation import DashboardResponse, EvaluationResponse
from app.services.evaluation_service import EvaluationService, EvaluationServiceError

router = APIRouter(tags=["evaluations"])


def _error_response(exc: EvaluationServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc), "code": exc.code},
    )


@router.post(
    "/prompts/{prompt_id}/evaluate",
    response_model=EvaluationResponse,
    status_code=201,
)
async def evaluate_prompt(
    prompt_id: uuid.UUID,
    service: EvaluationService = Depends(get_evaluation_service),
):
    try:
        return await service.trigger_evaluation(prompt_id)
    except EvaluationServiceError as exc:
        return _error_response(exc)


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
def get_evaluation(
    evaluation_id: uuid.UUID,
    service: EvaluationService = Depends(get_evaluation_service),
):
    try:
        return service.get_evaluation(evaluation_id)
    except EvaluationServiceError as exc:
        return _error_response(exc)


@router.get("/evaluations/dashboard", response_model=DashboardResponse)
def get_dashboard(
    category: PromptCategory | None = None,
    service: EvaluationService = Depends(get_evaluation_service),
):
    return service.get_dashboard(category)
