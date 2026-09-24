from __future__ import annotations

from typing import Any, Dict, List
from models.evidence import UncertaintyAssessment


class UncertaintyEngine:
    """
    Computes Information Completeness Index (ICI), Risk Score, Confidence,
    and determines whether enough evidence exists to act defensively or if
    step-up verification is required.
    """

    @staticmethod
    def assess_uncertainty(
        initial_risk: float,
        graph_signals: Dict[str, Any],
        step_up_completed: bool = False,
        step_up_status: str = "PENDING",
    ) -> UncertaintyAssessment:
        missing_signals: List[str] = []
        available_signal_points = 0.0
        total_possible_signal_points = 5.0

        # 1. Device identity signal
        if graph_signals.get("device_id"):
            available_signal_points += 1.0
        else:
            missing_signals.append("Missing Device Fingerprint")

        # 2. IP & Geolocation signal
        if graph_signals.get("ip_id"):
            available_signal_points += 1.0
        else:
            missing_signals.append("Missing Geolocation/IP Intelligence")

        # 3. Graph Cluster / Shared Ring intelligence
        if "shared_device_count" in graph_signals:
            available_signal_points += 1.0
        else:
            missing_signals.append("Missing Graph Ring Analysis")

        # 4. Transaction Historical Velocity
        if "card_velocity_15m" in graph_signals:
            available_signal_points += 1.0
        else:
            missing_signals.append("Missing Velocity Baseline")

        # 5. Direct Customer / Cardholder Confirmation
        if step_up_completed:
            available_signal_points += 1.0
        else:
            missing_signals.append("Unconfirmed Cardholder Authorization")

        ici = available_signal_points / total_possible_signal_points

        # Calculate adjusted risk score based on graph evidence
        risk = initial_risk
        if graph_signals.get("mule_ring_detected"):
            risk = max(risk, 95.0)
        elif graph_signals.get("micro_auth_spinning"):
            risk = max(risk, 90.0)
        elif graph_signals.get("is_new_device") and graph_signals.get("foreign_ip"):
            risk = max(risk, 82.0)

        if step_up_status == "CONFIRMED_LEGITIMATE":
            risk = min(risk, 20.0)
        elif step_up_status in ["TIMEOUT_NO_RESPONSE", "FAILED_VERIFICATION", "CONFIRMED_FRAUD"]:
            risk = min(100.0, risk + 25.0)

        # Confidence calculation
        confidence = round(0.5 + (0.5 * ici), 3)

        # Decision thresholds:
        # If risk is extreme (> 92) or very low (< 30) or step-up already completed, we can defensively act.
        # Otherwise (ambiguous/uncertain zone 40 - 90 without cardholder confirmation), step-up is required.
        requires_step_up = not step_up_completed and (45.0 <= risk < 92.0)
        can_defensively_act = step_up_completed or (risk >= 92.0) or (risk <= 30.0)

        if requires_step_up:
            reasoning = f"Risk score ({risk:.1f}) is elevated but ambiguous (ICI: {ici:.2f}). Additional evidence needed from cardholder before defensible blocking/clearing."
        elif can_defensively_act:
            reasoning = f"Information completeness ({ici:.2f}) and risk score ({risk:.1f}) provide sufficient defensibility to finalize case action."
        else:
            reasoning = f"Sufficient initial signals present for immediate administrative handling."

        return UncertaintyAssessment(
            information_completeness_index=round(ici, 2),
            risk_score=round(risk, 1),
            confidence=confidence,
            missing_critical_signals=missing_signals,
            can_defensively_act=can_defensively_act,
            requires_step_up=requires_step_up,
            reasoning=reasoning,
        )
