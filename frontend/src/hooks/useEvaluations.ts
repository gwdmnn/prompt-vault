import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { evaluationKeys } from "../lib/queryKeys";
import { promptKeys } from "../lib/queryKeys";
import { evaluationService } from "../services/evaluationService";
import type { PromptCategory } from "../types/prompt";

export function useEvaluationDetail(evaluationId: string) {
  return useQuery({
    queryKey: evaluationKeys.detail(evaluationId),
    queryFn: () => evaluationService.getById(evaluationId),
    enabled: !!evaluationId,
  });
}

export function useTriggerEvaluation(promptId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => evaluationService.trigger(promptId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: promptKeys.detail(promptId) });
      qc.invalidateQueries({ queryKey: evaluationKeys.dashboard() });
    },
  });
}

export function useEvaluationDashboard(category?: PromptCategory) {
  const queryKey = category
    ? evaluationKeys.dashboardByCategory(category)
    : evaluationKeys.dashboard();
  return useQuery({
    queryKey,
    queryFn: () => evaluationService.getDashboard(category),
  });
}
