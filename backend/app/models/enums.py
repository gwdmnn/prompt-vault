from enum import Enum


class PromptCategory(str, Enum):
    ORCHESTRATOR = "orchestrator"
    TASK_EXECUTION = "task_execution"


class EvaluationStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
