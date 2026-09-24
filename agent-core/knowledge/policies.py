from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel


class PolicyRule(BaseModel):
    rule_id: str
    title: str
    category: str
    condition_description: str
    mandatory_action: str
    approval_requirement: str
    regulatory_reference: Optional[str] = None


BANK_FRAUD_POLICIES: List[PolicyRule] = [
    PolicyRule(
        rule_id="POL-ATO-001",
        title="High-Velocity Device / IP Discrepancy",
        category="Account Takeover",
        condition_description="Transaction originated from a newly observed device or proxy IP within 2 hours of password/profile change.",
        mandatory_action="REQUEST_STEP_UP_AUTH",
        approval_requirement="AUTOMATED",
        regulatory_reference="FFIEC Authentication in an Internet Banking Environment",
    ),
    PolicyRule(
        rule_id="POL-RING-002",
        title="Multi-Account Shared Device Ring",
        category="Syndicate / Device Sharing",
        condition_description="Device ID is linked to >= 3 distinct customer accounts with simultaneous transactions or chargeback history.",
        mandatory_action="FREEZE_ACCOUNT",
        approval_requirement="TIER_2_SENIOR_FRAUD_OFFICER",
        regulatory_reference="FinCEN Advisory FIN-2016-A005 (Cyber-Enabled Fraud)",
    ),
    PolicyRule(
        rule_id="POL-CARD-003",
        title="Card Testing / Micro-Auth Spinning Pattern",
        category="Card Fraud",
        condition_description=">= 3 low-value transactions (< $5.00) within 15 minutes followed by a high-value purchase attempt (> $250.00).",
        mandatory_action="BLOCK_TRANSACTION",
        approval_requirement="AUTOMATED",
        regulatory_reference="PCI-DSS Guideline 10.2 / Visa Rules on Card Spinning",
    ),
    PolicyRule(
        rule_id="POL-SAR-004",
        title="Mandatory BSA / FinCEN SAR Filing Threshold",
        category="Regulatory Compliance",
        condition_description="Confirmed or highly probable suspicious transaction aggregate exceeds $5,000 with unknown identity or $10,000 regardless of identification.",
        mandatory_action="FILE_SAR",
        approval_requirement="COMPLIANCE_DIRECTOR",
        regulatory_reference="31 CFR § 1020.320 (Reports of Suspicious Transactions)",
    ),
    PolicyRule(
        rule_id="POL-STEPUP-005",
        title="Step-Up Authentication Failure or Timeout",
        category="Verification Protocol",
        condition_description="Customer fails step-up challenge or prompt expires without verification while risk score is elevated (> 65).",
        mandatory_action="BLOCK_TRANSACTION",
        approval_requirement="TIER_1_ANALYST",
        regulatory_reference="Bank Fraud Defense Operational Standard 3.1",
    ),
    PolicyRule(
        rule_id="POL-CLEAR-006",
        title="Step-Up Verified Legitimate by Verified Cardholder",
        category="Resolution Protocol",
        condition_description="Cardholder completes multi-factor challenge and explicitly authorizes transaction.",
        mandatory_action="ALLOW_TRANSACTION",
        approval_requirement="AUTOMATED",
        regulatory_reference="Customer Protection & Friction Mitigation Standard",
    ),
    PolicyRule(
        rule_id="POL-SYNTH-007",
        title="Synthetic Identity & Fragment Stacking",
        category="Identity Fraud",
        condition_description="Account credentials share phone/SSN/email domain with high-risk delinquent accounts while card has minimal credit history.",
        mandatory_action="FREEZE_ACCOUNT",
        approval_requirement="TIER_2_SENIOR_FRAUD_OFFICER",
        regulatory_reference="Federal Reserve White Paper on Synthetic Identity Fraud",
    ),
]


def get_applicable_policies(category: Optional[str] = None) -> List[PolicyRule]:
    if not category:
        return BANK_FRAUD_POLICIES
    return [p for p in BANK_FRAUD_POLICIES if p.category.lower() == category.lower()]
