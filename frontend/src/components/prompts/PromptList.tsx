import { Link } from "react-router-dom";
import type { Prompt } from "../../types/prompt";
import { PromptCategory } from "../../types/prompt";

interface PromptListProps {
  prompts: Prompt[];
}

const categoryLabels: Record<PromptCategory, string> = {
  [PromptCategory.ORCHESTRATOR]: "Orchestrator",
  [PromptCategory.TASK_EXECUTION]: "Task Execution",
};

const categoryColors: Record<PromptCategory, string> = {
  [PromptCategory.ORCHESTRATOR]: "bg-blue-100 text-blue-800",
  [PromptCategory.TASK_EXECUTION]: "bg-green-100 text-green-800",
};

export function PromptList({ prompts }: PromptListProps) {
  if (prompts.length === 0) {
    return (
      <div className="py-12 text-center text-sm text-gray-500">
        No prompts found. Create your first prompt to get started.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {prompts.map((prompt) => (
        <Link
          key={prompt.id}
          to={`/prompts/${prompt.id}`}
          className="block rounded-lg border border-gray-200 bg-white p-4 transition-colors hover:border-gray-300"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <h3 className="truncate font-medium text-gray-900">
                {prompt.title}
              </h3>
              {prompt.description && (
                <p className="mt-1 truncate text-sm text-gray-500">
                  {prompt.description}
                </p>
              )}
            </div>
            <span
              className={`inline-flex shrink-0 items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${categoryColors[prompt.category]}`}
            >
              {categoryLabels[prompt.category]}
            </span>
          </div>
          <div className="mt-3 flex items-center gap-4 text-xs text-gray-400">
            <span>v{prompt.version_count}</span>
            <span>
              Updated {new Date(prompt.updated_at).toLocaleDateString()}
            </span>
          </div>
        </Link>
      ))}
    </div>
  );
}
