import type { PromptVersion } from "../../types/prompt";

interface PromptVersionHistoryProps {
  versions: PromptVersion[];
  currentVersionNumber: number;
  onRestore: (versionNumber: number) => void;
  isRestoring: boolean;
}

export function PromptVersionHistory({
  versions,
  currentVersionNumber,
  onRestore,
  isRestoring,
}: PromptVersionHistoryProps) {
  if (versions.length === 0) {
    return <p className="text-sm text-gray-500">No version history available.</p>;
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-gray-700">Version History</h3>
      <div className="space-y-2">
        {versions.map((version) => (
          <div
            key={version.id}
            className={`rounded-lg border p-3 ${
              version.version_number === currentVersionNumber
                ? "border-gray-900 bg-gray-50"
                : "border-gray-200"
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <span className="text-sm font-medium text-gray-900">
                  Version {version.version_number}
                </span>
                {version.version_number === currentVersionNumber && (
                  <span className="ml-2 text-xs text-gray-500">(current)</span>
                )}
              </div>
              {version.version_number !== currentVersionNumber && (
                <button
                  onClick={() => onRestore(version.version_number)}
                  disabled={isRestoring}
                  className="rounded px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-100 disabled:opacity-50"
                >
                  Restore
                </button>
              )}
            </div>
            {version.change_summary && (
              <p className="mt-1 text-xs text-gray-500">{version.change_summary}</p>
            )}
            <p className="mt-1 text-xs text-gray-400">
              {new Date(version.created_at).toLocaleString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
