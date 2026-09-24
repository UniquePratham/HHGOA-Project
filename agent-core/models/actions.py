from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    ALLOW_TRANSACTION = "ALLOW_TRANSACTION"
    BLOCK_TRANSACTION = "BLOCK_TRANSACTION"
    MONITOR_ACCOUNT = "MONITOR_ACCOUNT"
    FREEZE_ACCOUNT = "FREEZE_ACCOUNT"
    WARN_CUSTOMER = "WARN_CUSTOMER"
    REQUEST_STEP_UP_AUTH = "REQUEST_STEP_UP_AUTH"
    REQUEST_CUSTOMER_VERIFICATION = "REQUEST_CUSTOMER_VERIFICATION"
    ESCALATE_TO_SENIOR_ANALYST = "ESCALATE_TO_SENIOR_ANALYST"
    FILE_SAR = "FILE_SAR"
    DISMISS_FALSE_POSITIVE = "DISMISS_FALSE_POSITIVE"


class ApprovalRoute(str, Enum):
    AUTOMATED = "AUTOMATED"
    TIER_1_ANALYST = "TIER_1_ANALYST"
    TIER_2_SENIOR_FRAUD_OFFICER = "TIER_2_SENIOR_FRAUD_OFFICER"
    COMPLIANCE_DIRECTOR = "COMPLIANCE_DIRECTOR"


class NextBestAction(BaseModel):
    milestone: str  # "MILESTONE_A_PRE_EVIDENCE" or "MILESTONE_B_POST_EVIDENCE"
    primary_action: ActionType
    secondary_actions: List[ActionType] = Field(default_factory=list)
    approval_route: ApprovalRoute
    defensibility_rationale: str
    policy_citation: str
    requires_human_signoff: bool = False
    estimated_impact: str
