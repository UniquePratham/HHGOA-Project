import pytest
from models.entities import Transaction, Card, Device, EgoGraph, GraphNode, GraphEdge, EntityType
from models.evidence import EvidenceCard, EvidenceType, Severity, UncertaintyAssessment
from models.actions import NextBestAction, ActionType, ApprovalRoute
from models.case import FraudCase, CaseTrigger, CaseStatus
from knowledge.policies import get_applicable_policies
from knowledge.typologies import KNOWN_FRAUD_TYPOLOGIES
from knowledge.graph_rag import GraphRAGRetriever


def test_models_creation():
    tx = Transaction(
        transaction_id="TX_1001",
        amount=1250.50,
        timestamp="2026-09-20T00:00:00Z",
        card_id="CARD_99",
        user_id="USER_01",
        model_risk_score=78.5,
    )
    assert tx.amount == 1250.50
    assert tx.model_risk_score == 78.5

    node = GraphNode(id="USER_01", label="User 01", entity_type=EntityType.USER, risk_level="HIGH")
    edge = GraphEdge(source="USER_01", target="CARD_99", relationship="OWNS")
    ego = EgoGraph(center_node_id="USER_01", nodes=[node], edges=[edge])
    assert len(ego.nodes) == 1
    assert ego.edges[0].relationship == "OWNS"


def test_evidence_and_actions():
    ev = EvidenceCard(
        id="EV_01",
        type=EvidenceType.OBSERVED_FACT,
        severity=Severity.HIGH,
        title="Shared Device Ring",
        description="Device connected to 5 accounts",
        source="TigerGraph GSQL",
        detected_at="2026-09-20T00:00:00Z",
        confidence=0.95,
    )
    assert ev.type == EvidenceType.OBSERVED_FACT

    nba = NextBestAction(
        milestone="MILESTONE_A_PRE_EVIDENCE",
        primary_action=ActionType.REQUEST_STEP_UP_AUTH,
        approval_route=ApprovalRoute.AUTOMATED,
        defensibility_rationale="Signal uncertain; verify with cardholder",
        policy_citation="POL-ATO-001",
        estimated_impact="Low friction",
    )
    assert nba.primary_action == ActionType.REQUEST_STEP_UP_AUTH


def test_graph_rag_grounding():
    retriever = GraphRAGRetriever()
    signals = {
        "shared_device_count": 5,
        "is_new_device": True,
        "foreign_ip": True,
        "amount": 6500.0,
        "has_cycles": True,
    }
    grounded = retriever.build_grounded_context("CASE_001", signals, risk_score=85.0)
    assert len(grounded["matched_typologies"]) >= 2
    assert grounded["sar_required"] is True
    assert len(grounded["applicable_policies"]) > 0
