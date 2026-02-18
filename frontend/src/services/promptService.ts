import { api } from "./api";
import type {
  PromptCreate,
  PromptDetail,
  PromptListResponse,
  PromptUpdate,
  PromptVersion,
} from "../types/prompt";
import type { PromptCategory } from "../types/prompt";

export interface ListPromptsParams {
  category?: PromptCategory;
  search?: string;
  page?: number;
  page_size?: number;
}

function buildQuery(params: ListPromptsParams): string {
  const sp = new URLSearchParams();
  if (params.category) sp.set("category", params.category);
  if (params.search) sp.set("search", params.search);
  if (params.page) sp.set("page", String(params.page));
  if (params.page_size) sp.set("page_size", String(params.page_size));
  const qs = sp.toString();
  return qs ? `?${qs}` : "";
}

export const promptService = {
  list(params: ListPromptsParams = {}): Promise<PromptListResponse> {
    return api.get<PromptListResponse>(`/api/prompts${buildQuery(params)}`);
  },

  get(promptId: string): Promise<PromptDetail> {
    return api.get<PromptDetail>(`/api/prompts/${promptId}`);
  },

  create(data: PromptCreate): Promise<PromptDetail> {
    return api.post<PromptDetail>("/api/prompts", data);
  },

  update(promptId: string, data: PromptUpdate): Promise<PromptDetail> {
    return api.put<PromptDetail>(`/api/prompts/${promptId}`, data);
  },

  delete(promptId: string): Promise<void> {
    return api.del<void>(`/api/prompts/${promptId}`);
  },

  listVersions(promptId: string): Promise<PromptVersion[]> {
    return api.get<PromptVersion[]>(`/api/prompts/${promptId}/versions`);
  },

  getVersion(promptId: string, versionNumber: number): Promise<PromptVersion> {
    return api.get<PromptVersion>(
      `/api/prompts/${promptId}/versions/${versionNumber}`,
    );
  },

  restoreVersion(promptId: string, versionNumber: number): Promise<PromptVersion> {
    return api.post<PromptVersion>(
      `/api/prompts/${promptId}/versions/${versionNumber}/restore`,
    );
  },
};
