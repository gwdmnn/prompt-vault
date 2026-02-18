import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { promptKeys, type PromptListFilters } from "../lib/queryKeys";
import {
  promptService,
  type ListPromptsParams,
} from "../services/promptService";
import type { PromptCreate, PromptUpdate } from "../types/prompt";

// ── Queries ──────────────────────────────────────────────────────

export function usePromptList(filters: PromptListFilters = {}) {
  return useQuery({
    queryKey: promptKeys.list(filters),
    queryFn: () =>
      promptService.list(filters as ListPromptsParams),
  });
}

export function usePromptDetail(promptId: string) {
  return useQuery({
    queryKey: promptKeys.detail(promptId),
    queryFn: () => promptService.get(promptId),
    enabled: !!promptId,
  });
}

export function usePromptVersions(promptId: string) {
  return useQuery({
    queryKey: promptKeys.versions(promptId),
    queryFn: () => promptService.listVersions(promptId),
    enabled: !!promptId,
  });
}

export function usePromptVersion(promptId: string, versionNumber: number) {
  return useQuery({
    queryKey: promptKeys.version(promptId, versionNumber),
    queryFn: () => promptService.getVersion(promptId, versionNumber),
    enabled: !!promptId && versionNumber > 0,
  });
}

// ── Mutations ────────────────────────────────────────────────────

export function useCreatePrompt() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: PromptCreate) => promptService.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: promptKeys.lists() });
    },
  });
}

export function useUpdatePrompt(promptId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: PromptUpdate) => promptService.update(promptId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: promptKeys.detail(promptId) });
      qc.invalidateQueries({ queryKey: promptKeys.lists() });
      qc.invalidateQueries({ queryKey: promptKeys.versions(promptId) });
    },
  });
}

export function useDeletePrompt() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (promptId: string) => promptService.delete(promptId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: promptKeys.lists() });
    },
  });
}

export function useRestoreVersion(promptId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (versionNumber: number) =>
      promptService.restoreVersion(promptId, versionNumber),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: promptKeys.detail(promptId) });
      qc.invalidateQueries({ queryKey: promptKeys.versions(promptId) });
      qc.invalidateQueries({ queryKey: promptKeys.lists() });
    },
  });
}
