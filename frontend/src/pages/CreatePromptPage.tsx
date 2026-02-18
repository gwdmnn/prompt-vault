import { useNavigate } from "react-router-dom";
import { useCreatePrompt } from "../hooks/usePrompts";
import { PromptForm, type PromptFormData } from "../components/prompts/PromptForm";

export function CreatePromptPage() {
  const navigate = useNavigate();
  const createMutation = useCreatePrompt();

  const handleSubmit = (data: PromptFormData) => {
    createMutation.mutate(
      {
        title: data.title,
        description: data.description,
        content: data.content,
        category: data.category,
      },
      {
        onSuccess: (result) => {
          navigate(`/prompts/${result.id}`);
        },
      },
    );
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">New Prompt</h1>
      <div className="mt-6 rounded-lg border border-gray-200 bg-white p-6">
        <PromptForm
          onSubmit={handleSubmit}
          isSubmitting={createMutation.isPending}
          submitLabel="Create Prompt"
        />
        {createMutation.isError && (
          <p className="mt-4 text-sm text-red-500">
            Failed to create prompt. Please try again.
          </p>
        )}
      </div>
    </div>
  );
}
