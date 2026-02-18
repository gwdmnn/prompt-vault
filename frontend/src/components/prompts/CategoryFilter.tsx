import { PromptCategory } from "../../types/prompt";

interface CategoryFilterProps {
  selected: PromptCategory | undefined;
  onChange: (category: PromptCategory | undefined) => void;
}

const categories = [
  { value: undefined, label: "All" },
  { value: PromptCategory.ORCHESTRATOR, label: "Orchestrator" },
  { value: PromptCategory.TASK_EXECUTION, label: "Task Execution" },
] as const;

export function CategoryFilter({ selected, onChange }: CategoryFilterProps) {
  return (
    <div className="flex gap-2">
      {categories.map((cat) => (
        <button
          key={cat.label}
          onClick={() => onChange(cat.value)}
          className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
            selected === cat.value
              ? "bg-gray-900 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          {cat.label}
        </button>
      ))}
    </div>
  );
}
