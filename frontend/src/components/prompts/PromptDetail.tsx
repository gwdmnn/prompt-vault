import type { PromptDetail as PromptDetailType } from "../../types/prompt";
import { PromptCategory } from "../../types/prompt";

interface PromptDetailProps {
  prompt: PromptDetailType;
}

const categoryLabels: Record<PromptCategory, string> = {
  [PromptCategory.ORCHESTRATOR]: "Orchestrator",
  [PromptCategory.TASK_EXECUTION]: "Task Execution",
};

export function PromptDetail({ prompt }: PromptDetailProps) {
  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold text-gray-900">{prompt.title}</h2>
          <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
            {categoryLabels[prompt.category]}
          </span>
        </div>
        {prompt.description && (
          <p className="mt-2 text-sm text-gray-500">{prompt.description}</p>
        )}
        <div className="mt-3 flex items-center gap-4 text-xs text-gray-400">
          <span>Version {prompt.current_version?.version_number ?? "?"}</span>
          <span>{prompt.version_count} total versions</span>
          <span>Updated {new Date(prompt.updated_at).toLocaleString()}</span>
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-medium text-gray-700">Prompt Content</h3>
        <pre className="overflow-auto whitespace-pre-wrap rounded-lg border border-gray-200 bg-gray-50 p-4 font-mono text-sm text-gray-800">
          {prompt.current_version?.content}
        </pre>
      </div>
    </div>
  );
}
