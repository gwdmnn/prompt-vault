export enum EvaluationStatus {
  PENDING = "pending",
  COMPLETED = "completed",
  FAILED = "failed",
}

export interface EvaluationCriterion {
  criterion_name: string;
  score: number;
  feedback: string;
  improvement_suggestion: string;
}

export interface Evaluation {
  id: string;
  prompt_version_id: string;
  overall_score: number | null;
  status: EvaluationStatus;
  error_message: string | null;
  criteria: EvaluationCriterion[];
  created_at: string;
  completed_at: string | null;
}

export interface EvaluationSummary {
  id: string;
  overall_score: number | null;
  status: EvaluationStatus;
  created_at: string;
}

export interface CriteriaBreakdown {
  criterion_name: string;
  avg_score: number;
}

export interface CommonImprovement {
  criterion_name: string;
  occurrence_count: number;
  avg_score: number;
}

export interface CategoryDashboard {
  category: string;
  avg_score: number;
  evaluation_count: number;
  criteria_breakdown: CriteriaBreakdown[];
  common_improvements: CommonImprovement[];
}

export interface DashboardResponse {
  categories: CategoryDashboard[];
  total_evaluations: number;
}
