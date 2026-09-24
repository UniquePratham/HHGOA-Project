from __future__ import annotations

from typing import Any, Dict
from models.benchmark import BenchmarkAnswerFile, BenchmarkApprovalRoute, BenchmarkNextBestActionItem
from models.case import FraudCase
from .cases_dataset import BenchmarkCaseSpec


class BenchmarkEvaluator:
    """
    Evaluates benchmark test cases and builds the submission-ready answer file structure.
    """

    @staticmethod
    def build_answer_file(spec: BenchmarkCaseSpec, case: FraudCase) -> BenchmarkAnswerFile:
        nba_pre = case.nba_pre_evidence
        nba_post = case.nba_post_evidence

        pre_item = BenchmarkNextBestActionItem(
            action=nba_pre.primary_action.value if nba_pre else "ALLOW_TRANSACTION",
            rationale=nba_pre.defensibility_rationale if nba_pre else "Standard processing",
            approval_route=BenchmarkApprovalRoute(
                required_route=nba_pre.approval_route.value if nba_pre else "AUTOMATED",
                requires_human_approval=nba_pre.requires_human_signoff if nba_pre else False,
                approver_role=nba_pre.approval_route.value if nba_pre else "AUTOMATED",
            ),
        )

        post_item = BenchmarkNextBestActionItem(
            action=nba_post.primary_action.value if nba_post else "ALLOW_TRANSACTION",
            rationale=nba_post.defensibility_rationale if nba_post else "Standard processing",
            approval_route=BenchmarkApprovalRoute(
                required_route=nba_post.approval_route.value if nba_post else "AUTOMATED",
                requires_human_approval=nba_post.requires_human_signoff if nba_post else False,
                approver_role=nba_post.approval_route.value if nba_post else "AUTOMATED",
            ),
        )

        findings: list[dict[str, Any]] = []
        for ev in case.evidence:
            findings.append({
                "finding_id": ev.id,
                "type": ev.type.value,
                "severity": ev.severity.value,
                "title": ev.title,
                "description": ev.description,
                "confidence": ev.confidence,
                "source": ev.source,
            })

        decisions_taken = [
            f"Pre-evidence action: {pre_item.action} (Route: {pre_item.approval_route.required_route})",
            f"Step-up verification challenge issued: {case.step_up.challenge_type if case.step_up else 'N/A'}",
            f"Step-up response received: {case.step_up.response_status if case.step_up else 'N/A'}",
            f"Post-evidence action: {post_item.action} (Route: {post_item.approval_route.required_route})",
            f"Final case resolution: {case.status.value}",
        ]

        if case.sar and case.sar.filing_required:
            decisions_taken.append(f"Suspicious Activity Report draft created: {case.sar.sar_id}")

        sar_data = case.sar.model_dump() if case.sar else None

        return BenchmarkAnswerFile(
            case_id=f"HHG-{spec.benchmark_id:03d}",
            benchmark_id=spec.benchmark_id,
            investigation_record={
                "target_transaction": spec.transaction_id,
                "subject_user": spec.target_user,
                "subject_card": spec.target_card,
                "amount": spec.amount,
                "upstream_model_risk": spec.upstream_model_risk,
                "evaluated_typology": spec.expected_typology,
                "initial_trigger": case.trigger.model_dump(),
                "graph_risk_indicators": case.graph_risk_indicators,
                "uncertainty_pre_evidence": case.uncertainty_pre_evidence.model_dump() if case.uncertainty_pre_evidence else None,
                "uncertainty_post_evidence": case.uncertainty_post_evidence.model_dump() if case.uncertainty_post_evidence else None,
                "similar_past_cases_found": len(case.similar_past_cases),
            },
            evidence_gathered=[ev.model_dump() for ev in case.evidence],
            findings=findings,
            decisions_and_actions_taken=decisions_taken,
            written_to_graph=case.graph_write_back_status == "COMMITTED",
            graph_write_back_details={
                "case_vertex_id": case.case_id,
                "status": case.graph_write_back_status,
                "edges_written": len(case.suspect_transaction_ids),
                "graph_target": "FraudGraph",
            },
            suspicious_activity_report=sar_data,
            next_best_action_before_additional_evidence=pre_item,
            next_best_action_after_additional_evidence=post_item,
            metadata={
                "agent_version": "1.0.0",
                "rules_version": "1.0.0",
                "graph_gateway_mode": "fixture",
            },
        )
