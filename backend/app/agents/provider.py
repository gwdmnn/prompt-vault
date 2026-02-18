"""LLM provider abstraction using Python Protocol for dependency inversion."""

import logging
from typing import Protocol

from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)


class CriterionResult(BaseModel):
    criterion_name: str
    score: int
    feedback: str
    improvement_suggestion: str


class LLMProvider(Protocol):
    """Protocol for LLM providers. Implementations must provide evaluate_criterion."""

    async def evaluate_criterion(
        self,
        prompt_content: str,
        criterion_name: str,
        criterion_description: str,
        scoring_rubric: str,
    ) -> CriterionResult: ...


class AnthropicProvider:
    def __init__(self):
        from langchain_anthropic import ChatAnthropic

        self.llm = ChatAnthropic(
            model=settings.MODEL,
            api_key=settings.ANTHROPIC_API_KEY,
            max_tokens=1024,
        )

    async def evaluate_criterion(
        self,
        prompt_content: str,
        criterion_name: str,
        criterion_description: str,
        scoring_rubric: str,
    ) -> CriterionResult:
        return await _call_llm(
            self.llm, prompt_content, criterion_name, criterion_description, scoring_rubric
        )


class OpenAIProvider:
    def __init__(self):
        from langchain_openai import ChatOpenAI

        self.llm = ChatOpenAI(
            model=settings.MODEL,
            api_key=settings.OPENAI_API_KEY,
            max_tokens=1024,
        )

    async def evaluate_criterion(
        self,
        prompt_content: str,
        criterion_name: str,
        criterion_description: str,
        scoring_rubric: str,
    ) -> CriterionResult:
        return await _call_llm(
            self.llm, prompt_content, criterion_name, criterion_description, scoring_rubric
        )


class GeminiProvider:
    def __init__(self):
        from langchain_google_genai import ChatGoogleGenerativeAI

        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            max_output_tokens=1024,
        )

    async def evaluate_criterion(
        self,
        prompt_content: str,
        criterion_name: str,
        criterion_description: str,
        scoring_rubric: str,
    ) -> CriterionResult:
        return await _call_llm(
            self.llm, prompt_content, criterion_name, criterion_description, scoring_rubric
        )


async def _call_llm(
    llm,
    prompt_content: str,
    criterion_name: str,
    criterion_description: str,
    scoring_rubric: str,
) -> CriterionResult:
    """Shared LLM calling logic for all providers."""
    import json

    system_msg = (
        "You are a prompt quality evaluator. Evaluate the given prompt against "
        "a specific criterion. Return your assessment as JSON with these fields: "
        '"score" (integer 0-100), "feedback" (detailed evaluation), '
        '"improvement_suggestion" (actionable suggestion if score < 80, empty string otherwise).'
    )
    user_msg = (
        f"## Criterion: {criterion_name}\n"
        f"## Description: {criterion_description}\n"
        f"## Scoring Rubric:\n{scoring_rubric}\n\n"
        f"## Prompt to Evaluate:\n{prompt_content}\n\n"
        "Return ONLY valid JSON: "
        '{"score": <int>, "feedback": "<string>", "improvement_suggestion": "<string>"}'
    )

    response = await llm.ainvoke([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ])

    try:
        content = response.content
        # Try to parse JSON from the response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        data = json.loads(content.strip())

        return CriterionResult(
            criterion_name=criterion_name,
            score=max(0, min(100, int(data.get("score", 50)))),
            feedback=str(data.get("feedback", "")),
            improvement_suggestion=str(data.get("improvement_suggestion", "")),
        )
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.warning("Failed to parse LLM response for %s: %s", criterion_name, e)
        return CriterionResult(
            criterion_name=criterion_name,
            score=0,
            feedback=f"Evaluation failed: could not parse LLM response",
            improvement_suggestion="",
        )


def get_provider() -> LLMProvider:
    """Factory function to create the configured LLM provider."""
    provider_map = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
    }
    provider_cls = provider_map.get(settings.LLM_PROVIDER)
    if not provider_cls:
        raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")
    return provider_cls()
