"""LangGraph fan-out/fan-in evaluation agent.

Uses the Send API to evaluate all 6 criteria in parallel,
then aggregates results in a final node.
"""

import logging
import operator
from typing import Annotated, TypedDict

from langgraph.constants import Send
from langgraph.graph import END, StateGraph

from app.agents.criteria import EVALUATION_CRITERIA, EvaluationCriterionDef
from app.agents.provider import CriterionResult, LLMProvider

logger = logging.getLogger(__name__)


class EvaluationState(TypedDict):
    prompt_content: str
    criterion_results: Annotated[list[CriterionResult], operator.add]
    overall_score: float | None
    error_message: str | None


class CriterionState(TypedDict):
    prompt_content: str
    criterion: EvaluationCriterionDef
    provider: LLMProvider
    criterion_results: Annotated[list[CriterionResult], operator.add]


def _prepare_evaluation(state: EvaluationState) -> list[Send]:
    """Fan-out: create a Send for each criterion."""
    sends = []
    for criterion in EVALUATION_CRITERIA:
        sends.append(
            Send(
                "evaluate_criterion",
                {
                    "prompt_content": state["prompt_content"],
                    "criterion": criterion,
                    "criterion_results": [],
                },
            )
        )
    return sends


async def _evaluate_criterion(state: CriterionState) -> dict:
    """Evaluate a single criterion using the LLM provider."""
    criterion: EvaluationCriterionDef = state["criterion"]
    provider: LLMProvider = state["provider"]

    try:
        result = await provider.evaluate_criterion(
            prompt_content=state["prompt_content"],
            criterion_name=criterion.name,
            criterion_description=criterion.description,
            scoring_rubric=criterion.scoring_rubric,
        )
        return {"criterion_results": [result]}
    except Exception as e:
        logger.warning("Criterion %s evaluation failed: %s", criterion.name, e)
        return {
            "criterion_results": [
                CriterionResult(
                    criterion_name=criterion.name,
                    score=0,
                    feedback=f"Evaluation failed: {e}",
                    improvement_suggestion="",
                )
            ]
        }


def _aggregate_results(state: EvaluationState) -> dict:
    """Fan-in: compute overall score from individual criterion results."""
    results = state["criterion_results"]

    if not results:
        return {"overall_score": None, "error_message": "No criteria were evaluated"}

    successful = [r for r in results if r.score > 0 or "failed" not in r.feedback.lower()]
    if not successful:
        return {"overall_score": None, "error_message": "All criteria evaluations failed"}

    overall = sum(r.score for r in results) / len(results)
    return {"overall_score": round(overall, 2), "error_message": None}


def build_evaluation_graph(provider: LLMProvider) -> StateGraph:
    """Build the evaluation StateGraph with the given LLM provider."""
    graph = StateGraph(EvaluationState)

    # Inject provider into criterion evaluation
    async def evaluate_with_provider(state: CriterionState) -> dict:
        state_with_provider = {**state, "provider": provider}
        return await _evaluate_criterion(state_with_provider)

    graph.add_node("evaluate_criterion", evaluate_with_provider)
    graph.add_node("aggregate_results", _aggregate_results)

    graph.set_conditional_entry_point(_prepare_evaluation)
    graph.add_edge("evaluate_criterion", "aggregate_results")
    graph.add_edge("aggregate_results", END)

    return graph.compile()


async def run_evaluation(provider: LLMProvider, prompt_content: str) -> EvaluationState:
    """Run a full evaluation of a prompt against all criteria."""
    compiled = build_evaluation_graph(provider)
    result = await compiled.ainvoke(
        {
            "prompt_content": prompt_content,
            "criterion_results": [],
            "overall_score": None,
            "error_message": None,
        }
    )
    return result
