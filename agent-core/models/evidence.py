from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    OBSERVED_FACT = "OBSERVED_FACT"
    INFERENCE = "INFERENCE"
    RECOMMENDATION = "RECOMMENDATION"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvidenceCard(BaseModel):
    id: str
    type: EvidenceType
    severity: Severity
    title: str
    description: str
    source: str  # e.g., "TigerGraph GSQL - Shared Device Ring Query", "Bank Fraud Policy Section 4.2"
    detected_at: str
    confidence: float = Field(ge=0.0, le=1.0)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    affected_entities: List[str] = Field(default_factory=list)
    remediation_hint: Optional[str] = None


class UncertaintyAssessment(BaseModel):
    information_completeness_index: float = Field(ge=0.0, le=1.0)  # 0.0 missing info -> 1.0 full signals
    risk_score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0)
    missing_critical_signals: List[str] = Field(default_factory=list)
    can_defensively_act: bool = False
    requires_step_up: bool = False
    reasoning: str
