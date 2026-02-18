import type { EvaluationCriterion } from "../../types/evaluation";

interface CriterionScoreProps {
  criterion: EvaluationCriterion;
}

const criterionLabels: Record<string, string> = {
  clarity: "Clarity",
  specificity: "Specificity",
  structure: "Structure",
  context_setting: "Context Setting",
  output_format_guidance: "Output Format",
  constraint_definition: "Constraints",
};

function scoreColor(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 60) return "bg-yellow-500";
  return "bg-red-500";
}

export function CriterionScore({ criterion }: CriterionScoreProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">
          {criterionLabels[criterion.criterion_name] ?? criterion.criterion_name}
        </span>
        <span className="text-sm font-semibold text-gray-900">{criterion.score}</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className={`h-full rounded-full ${scoreColor(criterion.score)}`}
          style={{ width: `${criterion.score}%` }}
        />
      </div>
      <p className="text-xs text-gray-500">{criterion.feedback}</p>
    </div>
  );
}
