import { useState } from "react";
import { useEvaluationDashboard } from "../hooks/useEvaluations";
import { EvaluationDashboard } from "../components/evaluations/EvaluationDashboard";
import { CategoryFilter } from "../components/prompts/CategoryFilter";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import type { PromptCategory } from "../types/prompt";

export function DashboardPage() {
  const [category, setCategory] = useState<PromptCategory | undefined>();
  const { data, isLoading, error } = useEvaluationDashboard(category);

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Evaluation Dashboard</h1>
      </div>

      <div className="mt-6">
        <CategoryFilter selected={category} onChange={setCategory} />
      </div>

      <div className="mt-6">
        {isLoading ? (
          <LoadingSpinner className="py-12" />
        ) : error ? (
          <div className="py-12 text-center text-sm text-red-500">
            Failed to load dashboard data.
          </div>
        ) : data ? (
          <EvaluationDashboard
            categories={data.categories}
            totalEvaluations={data.total_evaluations}
          />
        ) : null}
      </div>
    </div>
  );
}
