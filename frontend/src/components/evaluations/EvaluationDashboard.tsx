import type { CategoryDashboard } from "../../types/evaluation";

interface EvaluationDashboardProps {
  categories: CategoryDashboard[];
  totalEvaluations: number;
}

const categoryLabels: Record<string, string> = {
  orchestrator: "Orchestrator",
  task_execution: "Task Execution",
};

function scoreColor(score: number): string {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-yellow-600";
  return "text-red-600";
}

function barColor(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 60) return "bg-yellow-500";
  return "bg-red-500";
}

export function EvaluationDashboard({
  categories,
  totalEvaluations,
}: EvaluationDashboardProps) {
  if (categories.length === 0) {
    return (
      <div className="py-12 text-center text-sm text-gray-500">
        No evaluations yet. Evaluate some prompts to see dashboard data.
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="text-sm text-gray-500">
        {totalEvaluations} total evaluation{totalEvaluations !== 1 ? "s" : ""}
      </div>

      {categories.map((cat) => (
        <div key={cat.category} className="rounded-lg border border-gray-200 bg-white p-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              {categoryLabels[cat.category] ?? cat.category}
            </h3>
            <div className="text-right">
              <span className={`text-2xl font-bold ${scoreColor(cat.avg_score)}`}>
                {Math.round(cat.avg_score)}
              </span>
              <span className="text-sm text-gray-500"> avg</span>
              <p className="text-xs text-gray-400">
                {cat.evaluation_count} evaluation{cat.evaluation_count !== 1 ? "s" : ""}
              </p>
            </div>
          </div>

          {cat.criteria_breakdown.length > 0 && (
            <div className="mt-4 space-y-3">
              <h4 className="text-sm font-medium text-gray-700">Criteria Breakdown</h4>
              {cat.criteria_breakdown.map((cb) => (
                <div key={cb.criterion_name} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-600">
                      {cb.criterion_name.replace(/_/g, " ")}
                    </span>
                    <span className="font-medium text-gray-900">
                      {Math.round(cb.avg_score)}
                    </span>
                  </div>
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-200">
                    <div
                      className={`h-full rounded-full ${barColor(cb.avg_score)}`}
                      style={{ width: `${cb.avg_score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {cat.common_improvements.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700">Common Improvement Areas</h4>
              <ul className="mt-2 space-y-1">
                {cat.common_improvements.map((ci) => (
                  <li key={ci.criterion_name} className="flex items-center justify-between text-xs">
                    <span className="text-amber-700">
                      {ci.criterion_name.replace(/_/g, " ")}
                    </span>
                    <span className="text-gray-500">
                      {ci.occurrence_count}x below 80 (avg {Math.round(ci.avg_score)})
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
