from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .actions import NextBestAction
from .entities import EgoGraph
from .evidence import EvidenceCard, UncertaintyAssessment


class CaseStatus(str, Enum):
    TRIGGERED = "TRIGGERED"
    INVESTIGATING = "INVESTIGATING"
    AWAITING_SECONDARY_EVIDENCE = "AWAITING_SECONDARY_EVIDENCE"
    EVIDENCE_RECEIVED = "EVIDENCE_RECEIVED"
    DEFENSIBLE_DECISION_REACHED = "DEFENSIBLE_DECISION_REACHED"
    ESCALATED = "ESCALATED"
    RESOLVED_CONFIRMED_FRAUD = "RESOLVED_CONFIRMED_FRAUD"
    RESOLVED_CLEARED = "RESOLVED_CLEARED"


class CaseTrigger(BaseModel):
    trigger_type: str  # "HIGH_RISK_SCORE", "CUSTOMER_DISPUTE", "ANALYST_QUERY", "VELOCITY_SPIKE"
    source_id: str  # e.g., Transaction ID or Account ID
    initial_score: float
    description: str
    timestamp: str


class StepUpInteraction(BaseModel):
    challenge_type: str  # "SMS_OTP", "BIOMETRIC_PUSH", "ANALYST_PHONE_CALL", "CARD_VERIFICATION"
    sent_at: str
    responded_at: Optional[str] = None
    response_status: str  # "PENDING", "CONFIRMED_LEGITIMATE", "CONFIRMED_FRAUD", "TIMEOUT_NO_RESPONSE", "FAILED_VERIFICATION"
    notes: Optional[str] = None


class SuspiciousActivityReport(BaseModel):
    sar_id: str
    filing_required: bool
    filing_reason: str
    fin_cen_category: str  # e.g., "Structuring / Smurfing", "Identity Theft", "Unauthorized Electronic Fund Transfer"
    narrative: str
    primary_subjects: List[str]
    suspect_transactions: List[str]
    total_dollar_amount: float
    generated_at: str
    compliance_signoff_needed: bool = True


class TimelineEvent(BaseModel):
    timestamp: str
    stage: str
    title: str
    description: str
    actor: str = "System"  # System, Agent, Analyst, Cardholder
    status: str = "SUCCESS"  # SUCCESS, WARNING, ALERT, INFO


class FraudCase(BaseModel):
    case_id: str
    title: str
    status: CaseStatus = CaseStatus.TRIGGERED
    trigger: CaseTrigger
    subject_user_id: str
    subject_card_id: Optional[str] = None
    suspect_transaction_ids: List[str] = Field(default_factory=list)
    created_at: str
    updated_at: str
    timeline: List[TimelineEvent] = Field(default_factory=list)
    
    # Ego-net and graph metrics
    ego_graph: Optional[EgoGraph] = None
    graph_risk_indicators: Dict[str, Any] = Field(default_factory=dict)
    
    # Evidence and Uncertainty
    evidence: List[EvidenceCard] = Field(default_factory=list)
    uncertainty_pre_evidence: Optional[UncertaintyAssessment] = None
    uncertainty_post_evidence: Optional[UncertaintyAssessment] = None
    
    # Controlled step-up simulation
    step_up: Optional[StepUpInteraction] = None
    
    # Dual-Stage Actions
    nba_pre_evidence: Optional[NextBestAction] = None
    nba_post_evidence: Optional[NextBestAction] = None
    
    # Regulatory & Memory
    sar: Optional[SuspiciousActivityReport] = None
    similar_past_cases: List[Dict[str, Any]] = Field(default_factory=list)
    graph_write_back_status: str = "PENDING"  # PENDING, COMMITTED
