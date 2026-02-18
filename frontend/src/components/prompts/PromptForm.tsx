import { useState } from "react";
import { PromptCategory } from "../../types/prompt";

export interface PromptFormData {
  title: string;
  description: string;
  content: string;
  category: PromptCategory;
  change_summary?: string;
}

interface PromptFormProps {
  initialData?: Partial<PromptFormData>;
  onSubmit: (data: PromptFormData) => void;
  isSubmitting: boolean;
  submitLabel: string;
  showChangeSummary?: boolean;
}

export function PromptForm({
  initialData,
  onSubmit,
  isSubmitting,
  submitLabel,
  showChangeSummary = false,
}: PromptFormProps) {
  const [title, setTitle] = useState(initialData?.title ?? "");
  const [description, setDescription] = useState(initialData?.description ?? "");
  const [content, setContent] = useState(initialData?.content ?? "");
  const [category, setCategory] = useState<PromptCategory>(
    initialData?.category ?? PromptCategory.TASK_EXECUTION,
  );
  const [changeSummary, setChangeSummary] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      title,
      description,
      content,
      category,
      ...(showChangeSummary ? { change_summary: changeSummary } : {}),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Title
        </label>
        <input
          id="title"
          type="text"
          required
          maxLength={200}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <input
          id="description"
          type="text"
          maxLength={2000}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
        />
      </div>

      <div>
        <label htmlFor="category" className="block text-sm font-medium text-gray-700">
          Category
        </label>
        <select
          id="category"
          value={category}
          onChange={(e) => setCategory(e.target.value as PromptCategory)}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
        >
          <option value={PromptCategory.ORCHESTRATOR}>Orchestrator</option>
          <option value={PromptCategory.TASK_EXECUTION}>Task Execution</option>
        </select>
      </div>

      <div>
        <label htmlFor="content" className="block text-sm font-medium text-gray-700">
          Prompt Content
        </label>
        <textarea
          id="content"
          required
          maxLength={50000}
          rows={12}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 font-mono text-sm focus:border-gray-500 focus:outline-none"
        />
        <p className="mt-1 text-xs text-gray-400">{content.length} / 50,000 characters</p>
      </div>

      {showChangeSummary && (
        <div>
          <label htmlFor="change_summary" className="block text-sm font-medium text-gray-700">
            Change Summary
          </label>
          <input
            id="change_summary"
            type="text"
            maxLength={500}
            value={changeSummary}
            onChange={(e) => setChangeSummary(e.target.value)}
            placeholder="Describe what changed..."
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
          />
        </div>
      )}

      <button
        type="submit"
        disabled={isSubmitting || !title.trim() || !content.trim()}
        className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
      >
        {isSubmitting ? "Saving..." : submitLabel}
      </button>
    </form>
  );
}
