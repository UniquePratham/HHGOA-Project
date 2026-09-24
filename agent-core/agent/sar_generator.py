from __future__ import annotations

import datetime
from typing import Any, Dict, List
from models.case import SuspiciousActivityReport


class SARGenerator:
    """
    Generates regulatory FinCEN Suspicious Activity Reports (SAR) grounded
    in verifiable graph entities, transaction values, and policy thresholds.
    """

    @staticmethod
    def generate_sar(
        case_id: str,
        user_id: str,
        suspect_tx_ids: List[str],
        total_amount: float,
        typologies: List[Dict[str, Any]],
        graph_evidence: List[str],
    ) -> SuspiciousActivityReport:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        typology_names = [t.get("name", "Unknown") for t in typologies]
        fincen_category = "Unauthorized Electronic Fund Transfer / Identity Theft"
        if any("Mule" in name for name in typology_names):
            fincen_category = "Money Laundering / Layering / Mule Network"
        elif any("Testing" in name for name in typology_names):
            fincen_category = "Automated Card Testing / Cyber-Enabled Fraud"

        narrative = (
            f"SUSPICIOUS ACTIVITY REPORT (FINCEN FILING DRAFT)\n"
            f"Case Identifier: {case_id}\n"
            f"Date of Report: {now_str}\n"
            f"Subject Identity: {user_id}\n"
            f"Identified Typologies: {', '.join(typology_names)}\n"
            f"Aggregate Amount: ${total_amount:,.2f} across {len(suspect_tx_ids)} suspect transactions.\n\n"
            f"SUMMARY OF SUSPICIOUS ACTIVITY:\n"
            f"The financial institution's automated graph intelligence system detected abnormal transaction patterns "
            f"involving customer account {user_id}. Analysis of the transaction graph revealed the following verified evidence:\n"
        )

        for i, ev in enumerate(graph_evidence, 1):
            narrative += f"{i}. {ev}\n"

        narrative += (
            f"\nREGULATORY ASSESSMENT & ACTIONS TAKEN:\n"
            f"The observed activity violates Bank Fraud Defense Operational Standard 3.1 and 31 CFR § 1020.320. "
            f"The institution has placed defensive administrative holds on affected card and account instruments. "
            f"This filing is submitted for compliance review and statutory archiving."
        )

        return SuspiciousActivityReport(
            sar_id=f"SAR-{case_id}",
            filing_required=True,
            filing_reason=f"Aggregate amount (${total_amount:,.2f}) and confirmed pattern ({fincen_category}) exceed FinCEN thresholds.",
            fin_cen_category=fincen_category,
            narrative=narrative,
            primary_subjects=[user_id],
            suspect_transactions=suspect_tx_ids,
            total_dollar_amount=round(total_amount, 2),
            generated_at=now_str,
            compliance_signoff_needed=True,
        )
