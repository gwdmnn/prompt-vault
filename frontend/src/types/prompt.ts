export enum PromptCategory {
  ORCHESTRATOR = "orchestrator",
  TASK_EXECUTION = "task_execution",
}

export interface PromptVersion {
  id: string;
  prompt_id: string;
  version_number: number;
  content: string;
  change_summary: string;
  created_at: string;
}

export interface Prompt {
  id: string;
  title: string;
  description: string;
  category: PromptCategory;
  is_active: boolean;
  lock_version: number;
  created_at: string;
  updated_at: string;
  version_count: number;
}

export interface PromptDetail extends Prompt {
  current_version: PromptVersion;
  latest_evaluation?: {
    id: string;
    overall_score: number | null;
    status: string;
    created_at: string;
  };
}

export interface PromptListResponse {
  items: Prompt[];
  total: number;
  page: number;
  page_size: number;
}

export interface PromptCreate {
  title: string;
  description?: string;
  content: string;
  category: PromptCategory;
}

export interface PromptUpdate {
  title?: string;
  description?: string;
  content?: string;
  category?: PromptCategory;
  change_summary?: string;
  lock_version: number;
}
