from __future__ import annotations

from typing import Any, Dict, List, Optional
from .policies import BANK_FRAUD_POLICIES, PolicyRule
from .typologies import KNOWN_FRAUD_TYPOLOGIES, FraudTypology


class GraphRAGRetriever:
    """
    Grounds agent reasoning by combining structural graph evidence
    (topology, shared devices, cycles) with bank policies and documented fraud typologies.
    """

    def __init__(self) -> None:
        self.policies = BANK_FRAUD_POLICIES
        self.typologies = KNOWN_FRAUD_TYPOLOGIES

    def match_typologies(self, graph_signals: Dict[str, Any]) -> List[FraudTypology]:
        """
        Match detected graph and transaction signals against the 5 known fraud typologies.
        """
        matches: List[FraudTypology] = []
        
        shared_devices = graph_signals.get("shared_device_count", 1)
        is_new_device = graph_signals.get("is_new_device", False)
        has_cycles = graph_signals.get("has_cycles", False)
        card_velocity = graph_signals.get("card_velocity_15m", 1)
        amount = graph_signals.get("amount", 0.0)
        
        # ATO Check
        if is_new_device and (graph_signals.get("foreign_ip", False) or amount > 500.0):
            matches.append(self._get_typology("TYP-01"))
            
        # Card Testing Check
        if card_velocity >= 3 or graph_signals.get("micro_auth_spinning", False):
            matches.append(self._get_typology("TYP-02"))
            
        # Synthetic Identity Check
        if graph_signals.get("shared_identity_fragments", False) or shared_devices >= 4:
            matches.append(self._get_typology("TYP-03"))
            
        # Velocity Mule Ring Check
        if has_cycles or graph_signals.get("mule_ring_detected", False):
            matches.append(self._get_typology("TYP-04"))
            
        # Merchant Collusion Check
        if graph_signals.get("merchant_collusion_risk", False):
            matches.append(self._get_typology("TYP-05"))
            
        return matches

    def match_applicable_policies(
        self,
        typologies: List[FraudTypology],
        risk_score: float,
        step_up_status: Optional[str] = None,
        total_amount: float = 0.0,
    ) -> List[PolicyRule]:
        """
        Identify mandatory bank policies and regulatory mandates based on evidence.
        """
        matched: List[PolicyRule] = []
        
        # Check SAR requirement
        if total_amount >= 5000.0 and risk_score >= 70.0:
            sar_rule = next((p for p in self.policies if p.rule_id == "POL-SAR-004"), None)
            if sar_rule:
                matched.append(sar_rule)
                
        # Check Step-Up outcome
        if step_up_status == "CONFIRMED_LEGITIMATE":
            clear_rule = next((p for p in self.policies if p.rule_id == "POL-CLEAR-006"), None)
            if clear_rule:
                matched.append(clear_rule)
        elif step_up_status in ["TIMEOUT_NO_RESPONSE", "FAILED_VERIFICATION", "CONFIRMED_FRAUD"]:
            stepup_fail = next((p for p in self.policies if p.rule_id == "POL-STEPUP-005"), None)
            if stepup_fail:
                matched.append(stepup_fail)

        # Typology-driven rules
        for t in typologies:
            if t.typology_id == "TYP-01":
                p = next((x for x in self.policies if x.rule_id == "POL-ATO-001"), None)
                if p and p not in matched:
                    matched.append(p)
            elif t.typology_id == "TYP-02":
                p = next((x for x in self.policies if x.rule_id == "POL-CARD-003"), None)
                if p and p not in matched:
                    matched.append(p)
            elif t.typology_id in ["TYP-03", "TYP-04"]:
                p = next((x for x in self.policies if x.rule_id == "POL-RING-002"), None)
                if p and p not in matched:
                    matched.append(p)
                p2 = next((x for x in self.policies if x.rule_id == "POL-SYNTH-007"), None)
                if p2 and p2 not in matched:
                    matched.append(p2)

        return matched

    def build_grounded_context(
        self,
        case_id: str,
        graph_signals: Dict[str, Any],
        risk_score: float,
        step_up_status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Assemble the complete GraphRAG grounding bundle for the agent.
        """
        typologies = self.match_typologies(graph_signals)
        policies = self.match_applicable_policies(
            typologies=typologies,
            risk_score=risk_score,
            step_up_status=step_up_status,
            total_amount=graph_signals.get("amount", 0.0),
        )
        
        return {
            "case_id": case_id,
            "matched_typologies": [t.model_dump() for t in typologies],
            "applicable_policies": [p.model_dump() for p in policies],
            "graph_signals_summary": graph_signals,
            "sar_required": any(p.rule_id == "POL-SAR-004" for p in policies),
        }

    def _get_typology(self, typology_id: str) -> FraudTypology:
        return next((t for t in self.typologies if t.typology_id == typology_id), self.typologies[0])
