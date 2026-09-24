from __future__ import annotations

from typing import Any, Dict, List
from pydantic import BaseModel


class FraudTypology(BaseModel):
    typology_id: str
    name: str
    description: str
    graph_indicators: List[str]
    transaction_indicators: List[str]
    typical_risk_tier: str
    recommended_evidence_path: str


KNOWN_FRAUD_TYPOLOGIES: List[FraudTypology] = [
    FraudTypology(
        typology_id="TYP-01",
        name="Account Takeover (ATO)",
        description="Legitimate credentials compromised; unauthorized actor accesses account via new device/IP and initiates rapid fund drain or high-value purchase.",
        graph_indicators=[
            "Sudden new Device vertex attached to existing Account vertex",
            "IP address geolocation disparate from user historical cluster (> 500 miles)",
            "High degree centrality spike on new device within short temporal window",
        ],
        transaction_indicators=[
            "High transaction amount relative to account 30-day baseline (> 300%)",
            "Change of shipping address immediately prior to transaction",
            "Rapid succession of checkout attempts",
        ],
        typical_risk_tier="HIGH",
        recommended_evidence_path="Request Step-Up Biometric / SMS OTP auth to original verified cardholder phone.",
    ),
    FraudTypology(
        typology_id="TYP-02",
        name="Card Testing / Micro-Spinning",
        description="Automated scripts testing stolen credit card batches on digital merchants using low-dollar authorizations before executing large fraud orders.",
        graph_indicators=[
            "Multiple distinct Card vertices transacting sequentially from a single IP or Device vertex",
            "High out-degree from single digital checkout merchant node within minutes",
        ],
        transaction_indicators=[
            "Sequence of $1.00 - $4.99 charges",
            "High decline rate followed by single approved transaction",
            "Rapid interval (< 30 seconds between attempts)",
        ],
        typical_risk_tier="CRITICAL",
        recommended_evidence_path="Immediate automated card authorization block and merchant terminal velocity quarantine.",
    ),
    FraudTypology(
        typology_id="TYP-03",
        name="Synthetic Identity Fraud",
        description="Fabricated identity constructed by combining legitimate SSN fragments with fake names, shared email domains, and burner devices.",
        graph_indicators=[
            "Dense multi-card bipartite graph sharing same phone prefix or email domain",
            "Zero depth in historical credit graph; isolated cluster connecting only to burner devices",
        ],
        transaction_indicators=[
            "Bust-out pattern: Rapid maxing out of credit line following seasoning period",
            "Disposable domain email address",
        ],
        typical_risk_tier="HIGH",
        recommended_evidence_path="Freeze account and escalate to Tier-2 Fraud Officer for document re-verification.",
    ),
    FraudTypology(
        typology_id="TYP-04",
        name="Velocity Mule Ring / Smurfing",
        description="Network of connected collusive accounts moving funds rapidly in cyclic or layered paths to evade $5k/$10k BSA detection thresholds.",
        graph_indicators=[
            "Cycle topology in transaction sub-graph (A -> B -> C -> A)",
            "Shared IP/Device between sender and receiver entities",
            "High clustering coefficient among newly created accounts",
        ],
        transaction_indicators=[
            "Structured transfer amounts ($4,850, $4,900) just below CTR threshold",
            "Immediate withdrawal or secondary transfer after deposit",
        ],
        typical_risk_tier="CRITICAL",
        recommended_evidence_path="Freeze all accounts in detected component and file mandatory FinCEN SAR.",
    ),
    FraudTypology(
        typology_id="TYP-05",
        name="Merchant Collusion / Terminal Bust-Out",
        description="Dishonest merchant terminal collaborating with card fraud syndicate to process fraudulent transactions or fake refunds.",
        graph_indicators=[
            "Disproportionate edge count connecting to flagged high-risk card nodes",
            "Unusual geographic clustering of transacting cards from nationwide locations at single small merchant",
        ],
        transaction_indicators=[
            "Repeated round-dollar amounts ($500.00, $1,000.00)",
            "Excessive chargeback ratio (> 1.5%)",
        ],
        typical_risk_tier="HIGH",
        recommended_evidence_path="Hold merchant settlements, block subsequent transactions, escalate to compliance.",
    ),
]
