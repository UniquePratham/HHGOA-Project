from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class BenchmarkApprovalRoute(BaseModel):
    required_route: str
    requires_human_approval: bool
    approver_role: str


class BenchmarkNextBestActionItem(BaseModel):
    action: str
    rationale: str
    approval_route: BenchmarkApprovalRoute


class BenchmarkAnswerFile(BaseModel):
    case_id: str
    benchmark_id: int  # 1 to 20
    investigation_record: Dict[str, Any]
    evidence_gathered: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]
    decisions_and_actions_taken: List[str]
    written_to_graph: bool
    graph_write_back_details: Dict[str, Any]
    suspicious_activity_report: Optional[Dict[str, Any]] = None
    next_best_action_before_additional_evidence: BenchmarkNextBestActionItem
    next_best_action_after_additional_evidence: BenchmarkNextBestActionItem
    metadata: Dict[str, Any] = Field(default_factory=dict)
