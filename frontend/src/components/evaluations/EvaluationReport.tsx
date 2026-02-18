import type { Evaluation } from "../../types/evaluation";
import { EvaluationStatus } from "../../types/evaluation";
import { CriterionScore } from "./CriterionScore";
import { ImprovementSuggestions } from "./ImprovementSuggestions";

interface EvaluationReportProps {
  evaluation: Evaluation;
}

export function EvaluationReport({ evaluation }: EvaluationReportProps) {
  if (evaluation.status === EvaluationStatus.FAILED) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 p-4">
        <h3 className="text-sm font-medium text-red-800">Evaluation Failed</h3>
        <p className="mt-1 text-xs text-red-600">
          {evaluation.error_message ?? "An unknown error occurred."}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">Evaluation Report</h3>
        {evaluation.overall_score != null && (
          <div className="text-right">
            <span className="text-2xl font-bold text-gray-900">
              {Math.round(evaluation.overall_score)}
            </span>
            <span className="text-sm text-gray-500"> / 100</span>
          </div>
        )}
      </div>

      <div className="space-y-4">
        {evaluation.criteria.map((c) => (
          <CriterionScore key={c.criterion_name} criterion={c} />
        ))}
      </div>

      <ImprovementSuggestions criteria={evaluation.criteria} />

      <p className="text-xs text-gray-400">
        Evaluated on {new Date(evaluation.created_at).toLocaleString()}
      </p>
    </div>
  );
}
