from __future__ import annotations

from typing import Any, Dict, List, Optional
from models.actions import ActionType, ApprovalRoute, NextBestAction
from models.evidence import UncertaintyAssessment


class NextBestActionEngine:
    """
    Decides the Next Best Action and required approval route for:
    - Milestone A: Before additional evidence is requested
    - Milestone B: After additional evidence is received
    """

    @staticmethod
    def determine_nba_pre_evidence(
        uncertainty: UncertaintyAssessment,
        graph_signals: Dict[str, Any],
        grounded_context: Dict[str, Any],
    ) -> NextBestAction:
        risk = uncertainty.risk_score
        is_mule_ring = graph_signals.get("mule_ring_detected", False)
        is_micro_spin = graph_signals.get("micro_auth_spinning", False)

        # Extreme severe fraud syndicates do not wait for step-up
        if is_mule_ring or is_micro_spin or risk >= 92.0:
            return NextBestAction(
                milestone="MILESTONE_A_PRE_EVIDENCE",
                primary_action=ActionType.BLOCK_TRANSACTION,
                secondary_actions=[ActionType.FREEZE_ACCOUNT, ActionType.ESCALATE_TO_SENIOR_ANALYST],
                approval_route=ApprovalRoute.TIER_2_SENIOR_FRAUD_OFFICER,
                defensibility_rationale=f"Immediate critical graph pattern detected (Risk {risk:.1f}). Shared syndicate or automated micro-spinning requires immediate hard defense prior to customer outreach.",
                policy_citation="POL-RING-002: Multi-Account Shared Device Ring",
                requires_human_signoff=True,
                estimated_impact="High risk containment, card frozen, analyst review required.",
            )

        # Ambiguous / uncertain cases require step-up authentication
        if uncertainty.requires_step_up or (45.0 <= risk < 92.0):
            return NextBestAction(
                milestone="MILESTONE_A_PRE_EVIDENCE",
                primary_action=ActionType.REQUEST_STEP_UP_AUTH,
                secondary_actions=[ActionType.WARN_CUSTOMER],
                approval_route=ApprovalRoute.AUTOMATED,
                defensibility_rationale=f"Risk ({risk:.1f}) is elevated but identity is unconfirmed (ICI: {uncertainty.information_completeness_index:.2f}). Policy dictates step-up auth challenge before hard block.",
                policy_citation="POL-ATO-001: High-Velocity Device / IP Discrepancy",
                requires_human_signoff=False,
                estimated_impact="Friction applied to transaction pending customer response.",
            )

        # Clean / low risk transactions
        return NextBestAction(
            milestone="MILESTONE_A_PRE_EVIDENCE",
            primary_action=ActionType.ALLOW_TRANSACTION,
            secondary_actions=[ActionType.MONITOR_ACCOUNT],
            approval_route=ApprovalRoute.AUTOMATED,
            defensibility_rationale=f"Low initial risk ({risk:.1f}) and clean graph indicators warrant normal transaction authorization.",
            policy_citation="Standard Transaction Processing Policy",
            requires_human_signoff=False,
            estimated_impact="Zero customer friction.",
        )

    @staticmethod
    def determine_nba_post_evidence(
        step_up_status: str,
        uncertainty: UncertaintyAssessment,
        graph_signals: Dict[str, Any],
        grounded_context: Dict[str, Any],
    ) -> NextBestAction:
        risk = uncertainty.risk_score
        amount = graph_signals.get("amount", 0.0)

        # Customer verified legitimate
        if step_up_status == "CONFIRMED_LEGITIMATE":
            return NextBestAction(
                milestone="MILESTONE_B_POST_EVIDENCE",
                primary_action=ActionType.ALLOW_TRANSACTION,
                secondary_actions=[ActionType.DISMISS_FALSE_POSITIVE],
                approval_route=ApprovalRoute.AUTOMATED,
                defensibility_rationale="Cardholder successfully passed step-up verification and confirmed authorization of transaction.",
                policy_citation="POL-CLEAR-006: Step-Up Verified Legitimate by Verified Cardholder",
                requires_human_signoff=False,
                estimated_impact="Transaction approved, customer friction cleared.",
            )

        # Step-up failed, timed out, or customer reported fraud
        is_high_dollar = amount >= 5000.0 or risk >= 85.0
        secondary: List[ActionType] = [ActionType.FREEZE_ACCOUNT]
        if is_high_dollar:
            secondary.append(ActionType.FILE_SAR)

        approval = ApprovalRoute.COMPLIANCE_DIRECTOR if (is_high_dollar and ActionType.FILE_SAR in secondary) else ApprovalRoute.TIER_1_ANALYST

        return NextBestAction(
            milestone="MILESTONE_B_POST_EVIDENCE",
            primary_action=ActionType.BLOCK_TRANSACTION,
            secondary_actions=secondary,
            approval_route=approval,
            defensibility_rationale=f"Step-up status '{step_up_status}' confirms unauthorized attempt. Total amount ${amount:,.2f} with risk {risk:.1f} warrants blocking and policy remediation.",
            policy_citation="POL-STEPUP-005: Step-Up Authentication Failure or Timeout",
            requires_human_signoff=True,
            estimated_impact="Transaction blocked, card suspended, case progressed to resolution.",
        )
