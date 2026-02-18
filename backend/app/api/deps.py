from collections.abc import Generator

from fastapi import Depends
from sqlmodel import Session

from app.core.database import get_session
from app.repositories.prompt_repo import PromptRepository
from app.repositories.evaluation_repo import EvaluationRepository
from app.services.prompt_service import PromptService
from app.services.evaluation_service import EvaluationService


def get_db() -> Generator[Session, None, None]:
    yield from get_session()


def get_prompt_repository(session: Session = Depends(get_db)) -> PromptRepository:
    return PromptRepository(session)


def get_evaluation_repository(session: Session = Depends(get_db)) -> EvaluationRepository:
    return EvaluationRepository(session)


def get_prompt_service(repo: PromptRepository = Depends(get_prompt_repository)) -> PromptService:
    return PromptService(repo)


def get_evaluation_service(
    eval_repo: EvaluationRepository = Depends(get_evaluation_repository),
    prompt_repo: PromptRepository = Depends(get_prompt_repository),
) -> EvaluationService:
    return EvaluationService(eval_repo, prompt_repo)
