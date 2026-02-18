import logging
import uuid
from datetime import datetime, timezone

from app.agents.evaluator import run_evaluation
from app.agents.provider import get_provider
from app.models.enums import EvaluationStatus, PromptCategory
from app.models.evaluation import Evaluation, EvaluationCriterion
from app.repositories.evaluation_repo import EvaluationRepository
from app.repositories.prompt_repo import PromptRepository
from app.schemas.evaluation import (
    CategoryDashboard,
    CommonImprovement,
    CriteriaBreakdown,
    CriterionResponse,
    DashboardResponse,
    EvaluationResponse,
)

logger = logging.getLogger(__name__)


class EvaluationServiceError(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class EvaluationService:
    def __init__(self, eval_repo: EvaluationRepository, prompt_repo: PromptRepository):
        self.eval_repo = eval_repo
        self.prompt_repo = prompt_repo

    async def trigger_evaluation(self, prompt_id: uuid.UUID) -> EvaluationResponse:
        """Trigger evaluation of a prompt's current version."""
        prompt = self.prompt_repo.get_by_id(prompt_id)
        if not prompt:
            raise EvaluationServiceError(
                f"Prompt {prompt_id} not found", "NOT_FOUND", 404
            )
        if not prompt.current_version_id:
            raise EvaluationServiceError(
                "Prompt has no content version", "NO_VERSION", 400
            )

        # Create pending evaluation
        evaluation = Evaluation(prompt_version_id=prompt.current_version_id)
        evaluation = self.eval_repo.create(evaluation)

        try:
            provider = get_provider()
            result = await run_evaluation(provider, prompt.current_version.content)

            # Persist criterion results
            for cr in result.get("criterion_results", []):
                criterion = EvaluationCriterion(
                    evaluation_id=evaluation.id,
                    criterion_name=cr.criterion_name,
                    score=cr.score,
                    feedback=cr.feedback,
                    improvement_suggestion=cr.improvement_suggestion,
                )
                self.eval_repo.add_criterion(criterion)

            evaluation.overall_score = result.get("overall_score")
            evaluation.status = EvaluationStatus.COMPLETED
            evaluation.completed_at = datetime.now(timezone.utc)

            if result.get("error_message"):
                evaluation.error_message = result["error_message"]
                evaluation.status = EvaluationStatus.FAILED

        except Exception as e:
            logger.exception("Evaluation failed for prompt %s", prompt_id)
            evaluation.status = EvaluationStatus.FAILED
            evaluation.error_message = str(e)
            evaluation.completed_at = datetime.now(timezone.utc)

        self.eval_repo.update(evaluation)
        logger.info("Evaluation %s completed with status %s", evaluation.id, evaluation.status)

        return self._to_response(evaluation)

    def get_evaluation(self, evaluation_id: uuid.UUID) -> EvaluationResponse:
        evaluation = self.eval_repo.get_by_id(evaluation_id)
        if not evaluation:
            raise EvaluationServiceError(
                f"Evaluation {evaluation_id} not found", "NOT_FOUND", 404
            )
        return self._to_response(evaluation)

    def get_dashboard(self, category: PromptCategory | None = None) -> DashboardResponse:
        avg_rows = self.eval_repo.get_avg_scores_by_category(category)
        breakdown_rows = self.eval_repo.get_criteria_breakdown_by_category(category)
        improvement_rows = self.eval_repo.get_common_improvements_by_category(category)
        total = self.eval_repo.get_total_completed_count()

        # Group breakdowns and improvements by category
        breakdown_map: dict[PromptCategory, list[CriteriaBreakdown]] = {}
        for cat, crit_name, avg_score in breakdown_rows:
            breakdown_map.setdefault(cat, []).append(
                CriteriaBreakdown(criterion_name=crit_name, avg_score=round(avg_score, 2))
            )

        improvement_map: dict[PromptCategory, list[CommonImprovement]] = {}
        for cat, crit_name, count, avg_score in improvement_rows:
            improvement_map.setdefault(cat, []).append(
                CommonImprovement(
                    criterion_name=crit_name,
                    occurrence_count=count,
                    avg_score=round(avg_score, 2),
                )
            )

        categories = []
        for cat, avg_score, eval_count in avg_rows:
            categories.append(
                CategoryDashboard(
                    category=cat,
                    avg_score=round(avg_score, 2),
                    evaluation_count=eval_count,
                    criteria_breakdown=breakdown_map.get(cat, []),
                    common_improvements=improvement_map.get(cat, []),
                )
            )

        return DashboardResponse(categories=categories, total_evaluations=total)

    def _to_response(self, evaluation: Evaluation) -> EvaluationResponse:
        return EvaluationResponse(
            id=evaluation.id,
            prompt_version_id=evaluation.prompt_version_id,
            overall_score=evaluation.overall_score,
            status=evaluation.status,
            error_message=evaluation.error_message,
            criteria=[
                CriterionResponse.model_validate(c) for c in (evaluation.criteria or [])
            ],
            created_at=evaluation.created_at,
            completed_at=evaluation.completed_at,
        )
