import { api } from "./api";
import type { DashboardResponse, Evaluation } from "../types/evaluation";
import type { PromptCategory } from "../types/prompt";

export const evaluationService = {
  trigger(promptId: string): Promise<Evaluation> {
    return api.post<Evaluation>(`/api/prompts/${promptId}/evaluate`);
  },

  getById(evaluationId: string): Promise<Evaluation> {
    return api.get<Evaluation>(`/api/evaluations/${evaluationId}`);
  },

  getDashboard(category?: PromptCategory): Promise<DashboardResponse> {
    const qs = category ? `?category=${category}` : "";
    return api.get<DashboardResponse>(`/api/evaluations/dashboard${qs}`);
  },
};
