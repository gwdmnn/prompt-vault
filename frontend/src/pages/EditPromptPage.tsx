import { useNavigate, useParams } from "react-router-dom";
import { usePromptDetail, useUpdatePrompt } from "../hooks/usePrompts";
import { PromptForm, type PromptFormData } from "../components/prompts/PromptForm";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";

export function EditPromptPage() {
  const { promptId } = useParams<{ promptId: string }>();
  const navigate = useNavigate();
  const { data: prompt, isLoading } = usePromptDetail(promptId!);
  const updateMutation = useUpdatePrompt(promptId!);

  const handleSubmit = (data: PromptFormData) => {
    if (!prompt) return;
    updateMutation.mutate(
      {
        title: data.title,
        description: data.description,
        content: data.content,
        category: data.category,
        change_summary: data.change_summary,
        lock_version: prompt.lock_version,
      },
      {
        onSuccess: () => {
          navigate(`/prompts/${promptId}`);
        },
      },
    );
  };

  if (isLoading || !prompt) return <LoadingSpinner className="py-12" />;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Edit Prompt</h1>
      <div className="mt-6 rounded-lg border border-gray-200 bg-white p-6">
        <PromptForm
          initialData={{
            title: prompt.title,
            description: prompt.description,
            content: prompt.current_version?.content ?? "",
            category: prompt.category,
          }}
          onSubmit={handleSubmit}
          isSubmitting={updateMutation.isPending}
          submitLabel="Save Changes"
          showChangeSummary
        />
        {updateMutation.isError && (
          <p className="mt-4 text-sm text-red-500">
            Failed to update prompt. It may have been modified by another request.
          </p>
        )}
      </div>
    </div>
  );
}
