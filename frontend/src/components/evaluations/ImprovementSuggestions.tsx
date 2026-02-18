import type { EvaluationCriterion } from "../../types/evaluation";

interface ImprovementSuggestionsProps {
  criteria: EvaluationCriterion[];
}

const criterionLabels: Record<string, string> = {
  clarity: "Clarity",
  specificity: "Specificity",
  structure: "Structure",
  context_setting: "Context Setting",
  output_format_guidance: "Output Format",
  constraint_definition: "Constraints",
};

export function ImprovementSuggestions({ criteria }: ImprovementSuggestionsProps) {
  const lowScoring = criteria.filter(
    (c) => c.score < 80 && c.improvement_suggestion,
  );

  if (lowScoring.length === 0) {
    return (
      <p className="text-sm text-green-600">
        All criteria scored 80 or above. No improvements needed.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-gray-700">Improvement Suggestions</h4>
      <ul className="space-y-2">
        {lowScoring.map((c) => (
          <li
            key={c.criterion_name}
            className="rounded-md border border-amber-200 bg-amber-50 p-3"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-amber-800">
                {criterionLabels[c.criterion_name] ?? c.criterion_name}
              </span>
              <span className="text-xs text-amber-600">Score: {c.score}</span>
            </div>
            <p className="mt-1 text-xs text-amber-700">{c.improvement_suggestion}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
