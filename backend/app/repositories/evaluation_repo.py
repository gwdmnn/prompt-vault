import uuid

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.enums import EvaluationStatus, PromptCategory
from app.models.evaluation import Evaluation, EvaluationCriterion
from app.models.prompt import Prompt, PromptVersion


class EvaluationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, evaluation: Evaluation) -> Evaluation:
        self.session.add(evaluation)
        self.session.flush()
        return evaluation

    def get_by_id(self, evaluation_id: uuid.UUID) -> Evaluation | None:
        return self.session.get(Evaluation, evaluation_id)

    def add_criterion(self, criterion: EvaluationCriterion) -> EvaluationCriterion:
        self.session.add(criterion)
        self.session.flush()
        return criterion

    def update(self, evaluation: Evaluation) -> Evaluation:
        self.session.add(evaluation)
        self.session.flush()
        return evaluation

    def has_pending_for_prompt(self, prompt_id: uuid.UUID) -> bool:
        """Check if there's a pending evaluation for any version of this prompt."""
        stmt = (
            select(func.count())
            .select_from(Evaluation)
            .join(PromptVersion, Evaluation.prompt_version_id == PromptVersion.id)
            .where(
                PromptVersion.prompt_id == prompt_id,
                Evaluation.status == EvaluationStatus.PENDING,
            )
        )
        return self.session.exec(stmt).one() > 0

    def get_latest_for_version(self, prompt_version_id: uuid.UUID) -> Evaluation | None:
        stmt = (
            select(Evaluation)
            .where(Evaluation.prompt_version_id == prompt_version_id)
            .order_by(Evaluation.created_at.desc())  # type: ignore[union-attr]
            .limit(1)
        )
        return self.session.exec(stmt).first()

    # ── Dashboard aggregation queries ─────────────────────────────

    def get_avg_scores_by_category(
        self, category: PromptCategory | None = None
    ) -> list[tuple[PromptCategory, float, int]]:
        stmt = (
            select(
                Prompt.category,
                func.avg(Evaluation.overall_score).label("avg_score"),
                func.count(Evaluation.id).label("evaluation_count"),
            )
            .select_from(Evaluation)
            .join(PromptVersion, Evaluation.prompt_version_id == PromptVersion.id)
            .join(Prompt, PromptVersion.prompt_id == Prompt.id)
            .where(Evaluation.status == EvaluationStatus.COMPLETED, Prompt.is_active == True)  # noqa: E712
            .group_by(Prompt.category)
        )
        if category:
            stmt = stmt.where(Prompt.category == category)
        return list(self.session.exec(stmt).all())

    def get_criteria_breakdown_by_category(
        self, category: PromptCategory | None = None
    ) -> list[tuple[PromptCategory, str, float]]:
        stmt = (
            select(
                Prompt.category,
                EvaluationCriterion.criterion_name,
                func.avg(EvaluationCriterion.score).label("avg_score"),
            )
            .select_from(EvaluationCriterion)
            .join(Evaluation, EvaluationCriterion.evaluation_id == Evaluation.id)
            .join(PromptVersion, Evaluation.prompt_version_id == PromptVersion.id)
            .join(Prompt, PromptVersion.prompt_id == Prompt.id)
            .where(Evaluation.status == EvaluationStatus.COMPLETED, Prompt.is_active == True)  # noqa: E712
            .group_by(Prompt.category, EvaluationCriterion.criterion_name)
        )
        if category:
            stmt = stmt.where(Prompt.category == category)
        return list(self.session.exec(stmt).all())

    def get_common_improvements_by_category(
        self, category: PromptCategory | None = None
    ) -> list[tuple[PromptCategory, str, int, float]]:
        stmt = (
            select(
                Prompt.category,
                EvaluationCriterion.criterion_name,
                func.count().label("low_score_count"),
                func.avg(EvaluationCriterion.score).label("avg_score"),
            )
            .select_from(EvaluationCriterion)
            .join(Evaluation, EvaluationCriterion.evaluation_id == Evaluation.id)
            .join(PromptVersion, Evaluation.prompt_version_id == PromptVersion.id)
            .join(Prompt, PromptVersion.prompt_id == Prompt.id)
            .where(
                EvaluationCriterion.score < 80,
                Evaluation.status == EvaluationStatus.COMPLETED,
                Prompt.is_active == True,  # noqa: E712
            )
            .group_by(Prompt.category, EvaluationCriterion.criterion_name)
            .order_by(Prompt.category, func.count().desc())
        )
        if category:
            stmt = stmt.where(Prompt.category == category)
        return list(self.session.exec(stmt).all())

    def get_total_completed_count(self) -> int:
        stmt = select(func.count()).where(Evaluation.status == EvaluationStatus.COMPLETED)
        return self.session.exec(stmt).one()
