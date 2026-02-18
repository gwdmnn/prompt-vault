"""Evaluation criteria definitions.

Each criterion is defined with a name, description, and scoring rubric.
New criteria can be added by creating new instances — no modification to
evaluator code needed (Open/Closed Principle).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCriterionDef:
    name: str
    description: str
    scoring_rubric: str


EVALUATION_CRITERIA: list[EvaluationCriterionDef] = [
    EvaluationCriterionDef(
        name="clarity",
        description="How clear and unambiguous the prompt is",
        scoring_rubric=(
            "90-100: Single possible interpretation, precise language, no ambiguity.\n"
            "70-89: Mostly clear with minor ambiguities that don't affect execution.\n"
            "50-69: Several ambiguous instructions that could lead to different outputs.\n"
            "0-49: Vague, contradictory, or confusing instructions throughout."
        ),
    ),
    EvaluationCriterionDef(
        name="specificity",
        description="How detailed and specific the instructions are",
        scoring_rubric=(
            "90-100: Concrete parameters, well-defined scope, specific examples.\n"
            "70-89: Good detail with some areas that could be more specific.\n"
            "50-69: Overly broad in key areas, missing important constraints.\n"
            "0-49: Extremely vague, no concrete parameters or defined scope."
        ),
    ),
    EvaluationCriterionDef(
        name="structure",
        description="How well-organized the prompt is",
        scoring_rubric=(
            "90-100: Logical sections, clear flow, well-formatted with headers/lists.\n"
            "70-89: Good organization with minor flow issues.\n"
            "50-69: Partially organized but key sections are jumbled.\n"
            "0-49: No discernible structure, requirements are scattered."
        ),
    ),
    EvaluationCriterionDef(
        name="context_setting",
        description="How well background context is provided",
        scoring_rubric=(
            "90-100: Role, audience, domain, and background clearly stated.\n"
            "70-89: Good context with minor gaps in role or audience definition.\n"
            "50-69: Some context but missing critical background information.\n"
            "0-49: No context provided, assumes unstated knowledge."
        ),
    ),
    EvaluationCriterionDef(
        name="output_format_guidance",
        description="How clearly the expected output format is defined",
        scoring_rubric=(
            "90-100: Explicit format specified with examples, clear structure.\n"
            "70-89: Format described but could benefit from examples.\n"
            "50-69: Vague format guidance, output structure unclear.\n"
            "0-49: No format specified, output expectations undefined."
        ),
    ),
    EvaluationCriterionDef(
        name="constraint_definition",
        description="How well constraints and boundaries are defined",
        scoring_rubric=(
            "90-100: Clear limits, edge case handling, explicit do/don't rules.\n"
            "70-89: Good constraints with minor gaps in boundary cases.\n"
            "50-69: Some constraints but key boundaries are undefined.\n"
            "0-49: No constraints specified, unbounded scope."
        ),
    ),
]

CRITERION_NAMES = [c.name for c in EVALUATION_CRITERIA]
