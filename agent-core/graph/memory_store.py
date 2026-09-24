from __future__ import annotations

import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CaseMemoryItem(BaseModel):
    case_id: str
    title: str
    typology: str
    outcome: str  # "CONFIRMED_FRAUD", "CLEARED_FALSE_POSITIVE"
    final_action: str
    risk_score: float
    feature_vector: List[float] = Field(default_factory=list)
    key_indicators: List[str] = Field(default_factory=list)
    sar_filed: bool = False
    closed_month: int = 1  # 1 to 4


class CaseMemoryStore:
    """
    Historical investigation memory store indexing the 4 months of closed cases.
    Enables similarity search to inform agent decisions on new transactions.
    """

    def __init__(self) -> None:
        self._cases: Dict[str, CaseMemoryItem] = {}
        self._seed_historical_cases()

    def add_case(self, item: CaseMemoryItem) -> None:
        self._cases[item.case_id] = item

    def get_case(self, case_id: str) -> Optional[CaseMemoryItem]:
        return self._cases.get(case_id)

    def find_similar_cases(
        self,
        query_vector: List[float],
        top_k: int = 3,
        threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Cosine similarity search across historical closed case memory.
        """
        results: List[Dict[str, Any]] = []

        for c_id, item in self._cases.items():
            sim = self._cosine_similarity(query_vector, item.feature_vector)
            if sim >= threshold:
                results.append({
                    "case_id": item.case_id,
                    "title": item.title,
                    "typology": item.typology,
                    "outcome": item.outcome,
                    "final_action": item.final_action,
                    "similarity_score": round(sim, 4),
                    "key_indicators": item.key_indicators,
                    "sar_filed": item.sar_filed,
                })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def _seed_historical_cases(self) -> None:
        """
        Seeds 4 months of realistic closed cases representing confirmed fraud and cleared investigations.
        Features: [risk_score/100, is_new_device, shared_device_count/5, velocity/5, amount/5000, has_foreign_ip]
        """
        seed_data = [
            CaseMemoryItem(
                case_id="HIST-M1-001",
                title="Account Takeover via Russian Proxy",
                typology="Account Takeover",
                outcome="CONFIRMED_FRAUD",
                final_action="BLOCK_TRANSACTION",
                risk_score=92.0,
                feature_vector=[0.92, 1.0, 0.2, 0.4, 0.7, 1.0],
                key_indicators=["New Device", "Russian Proxy IP", "High Amount Burst"],
                sar_filed=True,
                closed_month=1,
            ),
            CaseMemoryItem(
                case_id="HIST-M1-002",
                title="Cleared Cardholder Travel Authorization",
                typology="Account Takeover",
                outcome="CLEARED_FALSE_POSITIVE",
                final_action="ALLOW_TRANSACTION",
                risk_score=68.0,
                feature_vector=[0.68, 1.0, 0.2, 0.2, 0.3, 1.0],
                key_indicators=["New Device", "Overseas Hotel Booking", "SMS 2FA Verified"],
                sar_filed=False,
                closed_month=1,
            ),
            CaseMemoryItem(
                case_id="HIST-M2-003",
                title="Micro-Spinning Bot Attack on Digital Goods",
                typology="Card Testing / Spinning",
                outcome="CONFIRMED_FRAUD",
                final_action="BLOCK_TRANSACTION",
                risk_score=95.0,
                feature_vector=[0.95, 0.0, 0.8, 1.0, 0.1, 0.0],
                key_indicators=["12 micro auths in 3 mins", "Shared Emulator Device", "High velocity"],
                sar_filed=False,
                closed_month=2,
            ),
            CaseMemoryItem(
                case_id="HIST-M3-004",
                title="Smurfing Mule Syndicate Across 6 Accounts",
                typology="Velocity Mule Ring",
                outcome="CONFIRMED_FRAUD",
                final_action="FREEZE_ACCOUNT",
                risk_score=98.0,
                feature_vector=[0.98, 0.0, 1.0, 0.8, 0.95, 0.0],
                key_indicators=["6 accounts shared 1 device", "Cycle transfers", "Total $28,500"],
                sar_filed=True,
                closed_month=3,
            ),
            CaseMemoryItem(
                case_id="HIST-M4-005",
                title="Family Member Card Sharing Cleared",
                typology="Syndicate / Device Sharing",
                outcome="CLEARED_FALSE_POSITIVE",
                final_action="ALLOW_TRANSACTION",
                risk_score=55.0,
                feature_vector=[0.55, 0.0, 0.4, 0.2, 0.1, 0.0],
                key_indicators=["Shared tablet between spouse cards", "Customer confirmed"],
                sar_filed=False,
                closed_month=4,
            ),
        ]

        for item in seed_data:
            self._cases[item.case_id] = item
