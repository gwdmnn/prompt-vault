import { useState } from "react";
import { Link } from "react-router-dom";
import { usePromptList } from "../hooks/usePrompts";
import { PromptList } from "../components/prompts/PromptList";
import { CategoryFilter } from "../components/prompts/CategoryFilter";
import { LoadingSpinner } from "../components/shared/LoadingSpinner";
import type { PromptCategory } from "../types/prompt";

export function PromptsPage() {
  const [category, setCategory] = useState<PromptCategory | undefined>();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading, error } = usePromptList({
    category,
    search: search || undefined,
    page,
    page_size: 20,
  });

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Prompts</h1>
        <Link
          to="/prompts/new"
          className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
        >
          New Prompt
        </Link>
      </div>

      <div className="mt-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <CategoryFilter selected={category} onChange={(c) => { setCategory(c); setPage(1); }} />
        <input
          type="text"
          placeholder="Search prompts..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
        />
      </div>

      <div className="mt-6">
        {isLoading ? (
          <LoadingSpinner className="py-12" />
        ) : error ? (
          <div className="py-12 text-center text-sm text-red-500">
            Failed to load prompts.
          </div>
        ) : data ? (
          <>
            <PromptList prompts={data.items} />
            {data.total > data.page_size && (
              <div className="mt-6 flex items-center justify-center gap-4">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                  className="rounded px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-500">
                  Page {data.page} of {Math.ceil(data.total / data.page_size)}
                </span>
                <button
                  disabled={page >= Math.ceil(data.total / data.page_size)}
                  onClick={() => setPage((p) => p + 1)}
                  className="rounded px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            )}
          </>
        ) : null}
      </div>
    </div>
  );
}
