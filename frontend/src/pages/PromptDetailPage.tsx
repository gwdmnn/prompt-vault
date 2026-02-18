import { Link, useNavigate, useParams } from "react-router-dom";
import {
  usePromptDetail,
  useDeletePrompt,
  usePromptVersions,
  useRestoreVersion,
} from "../hooks/usePrompts";
import { useTriggerEvaluation } from "../hooks/useEvaluations";
import { PromptDetail } from "../components/prompts/PromptDetail";
import { PromptVersionHistory } from "../components/prompts/PromptVersionHistory";
import { EvaluationReport } from "../components/evaluations/EvaluationReport";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import type { Evaluation } from "../types/evaluation";
import { useState } from "react";

export function PromptDetailPage() {
  const { promptId } = useParams<{ promptId: string }>();
  const navigate = useNavigate();
  const { data: prompt, isLoading, error } = usePromptDetail(promptId!);
  const { data: versions } = usePromptVersions(promptId!);
  const deleteMutation = useDeletePrompt();
  const restoreMutation = useRestoreVersion(promptId!);
  const evaluateMutation = useTriggerEvaluation(promptId!);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);

  const handleDelete = () => {
    if (!promptId || !confirm("Are you sure you want to delete this prompt?")) return;
    deleteMutation.mutate(promptId, {
      onSuccess: () => navigate("/"),
    });
  };

  const handleRestore = (versionNumber: number) => {
    restoreMutation.mutate(versionNumber);
  };

  const handleEvaluate = () => {
    evaluateMutation.mutate(undefined, {
      onSuccess: (result) => {
        setEvaluation(result);
      },
    });
  };

  if (isLoading) return <LoadingSpinner className="py-12" />;
  if (error || !prompt) {
    return (
      <div className="py-12 text-center text-sm text-red-500">
        Prompt not found.
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <Link to="/" className="text-sm text-gray-500 hover:text-gray-900">
          &larr; Back to prompts
        </Link>
        <div className="flex gap-3">
          <button
            onClick={handleEvaluate}
            disabled={evaluateMutation.isPending}
            className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {evaluateMutation.isPending ? "Evaluating..." : "Evaluate"}
          </button>
          <Link
            to={`/prompts/${promptId}/edit`}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Edit
          </Link>
          <button
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
            className="rounded-md border border-red-300 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
          >
            Delete
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <PromptDetail prompt={prompt} />
          </div>

          {evaluation && (
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <EvaluationReport evaluation={evaluation} />
            </div>
          )}
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <PromptVersionHistory
            versions={versions ?? []}
            currentVersionNumber={prompt.current_version?.version_number ?? 0}
            onRestore={handleRestore}
            isRestoring={restoreMutation.isPending}
          />
        </div>
      </div>
    </div>
  );
}
