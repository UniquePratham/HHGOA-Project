from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
from models.case import CaseStatus, CaseTrigger, FraudCase, StepUpInteraction, TimelineEvent
from models.evidence import EvidenceCard, EvidenceType, Severity
from graph.gateway import TigerGraphGateway
from knowledge.graph_rag import GraphRAGRetriever
from .actions_engine import NextBestActionEngine
from .sar_generator import SARGenerator
from .uncertainty import UncertaintyEngine


class InvestigationOrchestrator:
    """
    State machine driving the autonomous and human-in-the-loop fraud investigation:
    Trigger -> Graph Ingestion -> Ego-Graph Enrichment -> Pattern Detection ->
    Uncertainty Assessment -> Milestone A NBA -> Controlled Step-Up Simulation ->
    Milestone B NBA -> SAR Filing -> Graph Memory Commit.
    """

    def __init__(self, gateway: Optional[TigerGraphGateway] = None) -> None:
        self.gateway = gateway or TigerGraphGateway()
        self.retriever = GraphRAGRetriever()

    def run_full_investigation(
        self,
        transaction_id: str,
        initial_risk: Optional[float] = None,
        simulate_step_up_response: Optional[str] = None,
    ) -> FraudCase:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # 1. Trigger & Initial Ingestion
        tx_signals = self.gateway.get_transaction_signals(transaction_id)
        risk = initial_risk if initial_risk is not None else tx_signals.get("model_risk_score", 50.0)
        
        case_id = f"CASE-{transaction_id}"
        case = FraudCase(
            case_id=case_id,
            title=f"Investigation for {transaction_id}",
            status=CaseStatus.INVESTIGATING,
            trigger=CaseTrigger(
                trigger_type="HIGH_RISK_SCORE" if risk >= 70 else "ANALYST_QUERY",
                source_id=transaction_id,
                initial_score=risk,
                description=f"Transaction {transaction_id} flagged with model risk {risk:.1f}",
                timestamp=now_str,
            ),
            subject_user_id=tx_signals.get("user_id") or "UNKNOWN_USER",
            subject_card_id=tx_signals.get("card_id"),
            suspect_transaction_ids=[transaction_id],
            created_at=now_str,
            updated_at=now_str,
        )

        # 2. Graph Traversal & Ego-Net Extraction
        ego_graph = self.gateway.get_ego_graph(transaction_id, radius=2)
        case.ego_graph = ego_graph
        case.graph_risk_indicators = tx_signals

        # 3. Evidence Gathering (Observed Facts vs Inferences)
        evidence_list: List[EvidenceCard] = []

        if tx_signals.get("shared_device_count", 1) > 1:
            evidence_list.append(
                EvidenceCard(
                    id=f"EV-{case_id}-01",
                    type=EvidenceType.OBSERVED_FACT,
                    severity=Severity.CRITICAL if tx_signals.get("mule_ring_detected") else Severity.HIGH,
                    title="Shared Device Syndicate Detected",
                    description=f"Device {tx_signals.get('device_id')} is linked to {tx_signals.get('shared_device_count')} distinct accounts.",
                    source="TigerGraph GSQL: detect_shared_device_ring",
                    detected_at=now_str,
                    confidence=0.98,
                    raw_data={"device_id": tx_signals.get("device_id"), "count": tx_signals.get("shared_device_count")},
                    affected_entities=[tx_signals.get("user_id", "")] if tx_signals.get("user_id") else [],
                )
            )

        if tx_signals.get("foreign_ip"):
            evidence_list.append(
                EvidenceCard(
                    id=f"EV-{case_id}-02",
                    type=EvidenceType.OBSERVED_FACT,
                    severity=Severity.HIGH,
                    title="Anonymized Proxy / Tor IP Connection",
                    description=f"Transaction originated via suspicious routing node {tx_signals.get('ip_id')}.",
                    source="Network Intelligence IP Layer",
                    detected_at=now_str,
                    confidence=0.95,
                    raw_data={"ip_id": tx_signals.get("ip_id")},
                )
            )

        if tx_signals.get("micro_auth_spinning"):
            evidence_list.append(
                EvidenceCard(
                    id=f"EV-{case_id}-03",
                    type=EvidenceType.OBSERVED_FACT,
                    severity=Severity.CRITICAL,
                    title="Card Micro-Spinning Sequence Observed",
                    description="Sequence of low-dollar tests observed within a 15-minute window.",
                    source="Transaction Velocity Engine",
                    detected_at=now_str,
                    confidence=0.92,
                )
            )

        # GraphRAG Grounding
        grounded = self.retriever.build_grounded_context(case_id, tx_signals, risk)
        for t in grounded["matched_typologies"]:
            evidence_list.append(
                EvidenceCard(
                    id=f"EV-TYP-{t['typology_id']}",
                    type=EvidenceType.INFERENCE,
                    severity=Severity.HIGH,
                    title=f"Typology Match: {t['name']}",
                    description=t["description"],
                    source="GraphRAG Typology Knowledge Base",
                    detected_at=now_str,
                    confidence=0.88,
                    remediation_hint=t["recommended_evidence_path"],
                )
            )

        case.evidence = evidence_list

        # Search Historical Case Memory
        query_vec = [
            min(1.0, risk / 100.0),
            1.0 if tx_signals.get("is_new_device") else 0.0,
            min(1.0, tx_signals.get("shared_device_count", 1) / 5.0),
            1.0 if tx_signals.get("micro_auth_spinning") else 0.2,
            min(1.0, tx_signals.get("amount", 0.0) / 5000.0),
            1.0 if tx_signals.get("foreign_ip") else 0.0,
        ]
        case.similar_past_cases = self.gateway.memory_store.find_similar_cases(query_vec, top_k=2)

        # 4. Uncertainty Assessment (Pre-Evidence)
        uncertainty_pre = UncertaintyEngine.assess_uncertainty(
            initial_risk=risk,
            graph_signals=tx_signals,
            step_up_completed=False,
        )
        case.uncertainty_pre_evidence = uncertainty_pre

        # 5. Milestone A: Pre-Evidence Next Best Action & Route
        nba_pre = NextBestActionEngine.determine_nba_pre_evidence(
            uncertainty=uncertainty_pre,
            graph_signals=tx_signals,
            grounded_context=grounded,
        )
        case.nba_pre_evidence = nba_pre

        # 6. Controlled Secondary Evidence Simulation
        # If not provided, simulate according to scenario
        chosen_step_up_status = simulate_step_up_response
        if not chosen_step_up_status:
            if tx_signals.get("mule_ring_detected") or risk >= 90.0:
                chosen_step_up_status = "CONFIRMED_FRAUD"
            elif 45.0 <= risk < 90.0:
                chosen_step_up_status = "TIMEOUT_NO_RESPONSE" if "RING" in transaction_id else "CONFIRMED_LEGITIMATE"
            else:
                chosen_step_up_status = "CONFIRMED_LEGITIMATE"

        case.step_up = StepUpInteraction(
            challenge_type="SMS_OTP" if "SAFE" in transaction_id else "BIOMETRIC_PUSH",
            sent_at=now_str,
            responded_at=now_str,
            response_status=chosen_step_up_status,
            notes=f"Step-up challenge simulation completed with status: {chosen_step_up_status}",
        )

        # 7. Uncertainty Assessment (Post-Evidence) & Milestone B NBA
        uncertainty_post = UncertaintyEngine.assess_uncertainty(
            initial_risk=risk,
            graph_signals=tx_signals,
            step_up_completed=True,
            step_up_status=chosen_step_up_status,
        )
        case.uncertainty_post_evidence = uncertainty_post

        nba_post = NextBestActionEngine.determine_nba_post_evidence(
            step_up_status=chosen_step_up_status,
            uncertainty=uncertainty_post,
            graph_signals=tx_signals,
            grounded_context=grounded,
        )
        case.nba_post_evidence = nba_post

        # Final Status & SAR
        if nba_post.primary_action in ["BLOCK_TRANSACTION", "FREEZE_ACCOUNT"]:
            case.status = CaseStatus.RESOLVED_CONFIRMED_FRAUD
        else:
            case.status = CaseStatus.RESOLVED_CLEARED

        # Generate SAR if required by policy
        graph_evidence_summaries = [e.description for e in evidence_list if e.type == EvidenceType.OBSERVED_FACT]
        if "FILE_SAR" in [nba_post.primary_action] + [a.value for a in nba_post.secondary_actions] or grounded["sar_required"]:
            case.sar = SARGenerator.generate_sar(
                case_id=case_id,
                user_id=case.subject_user_id,
                suspect_tx_ids=case.suspect_transaction_ids,
                total_amount=tx_signals.get("amount", 0.0),
                typologies=grounded["matched_typologies"],
                graph_evidence=graph_evidence_summaries,
            )

        # 8. Commit Case to Graph Memory
        self.gateway.write_case_to_graph(
            case_id=case_id,
            title=case.title,
            outcome=case.status.value,
            risk_level="CRITICAL" if uncertainty_post.risk_score >= 80 else ("HIGH" if uncertainty_post.risk_score >= 60 else "LOW"),
            related_txs=case.suspect_transaction_ids,
        )
        case.graph_write_back_status = "COMMITTED"
        case.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 9. Build Verified Chronological Investigation Timeline
        timeline_events: List[TimelineEvent] = [
            TimelineEvent(
                timestamp=now_str,
                stage="TRIGGER",
                title="Investigation Initiated",
                description=f"Transaction {transaction_id} flagged with model risk score {risk:.1f}.",
                actor="Fraud Engine",
                status="ALERT" if risk >= 75 else "INFO",
            ),
            TimelineEvent(
                timestamp=now_str,
                stage="GRAPH_TRAVERSAL",
                title="TigerGraph Ego-Net Inspected",
                description=f"Extracted 2-hop neighborhood: {len(ego_graph.nodes)} vertices, {len(ego_graph.edges)} edges.",
                actor="TigerGraph GSQL",
                status="INFO",
            ),
        ]

        if tx_signals.get("shared_device_count", 1) > 1:
            timeline_events.append(
                TimelineEvent(
                    timestamp=now_str,
                    stage="PATTERN_DETECTION",
                    title="Shared Device Syndicate Detected",
                    description=f"Device {tx_signals.get('device_id')} linked across {tx_signals.get('shared_device_count')} accounts.",
                    actor="Graph Algorithm Suite",
                    status="ALERT",
                )
            )

        if case.similar_past_cases:
            timeline_events.append(
                TimelineEvent(
                    timestamp=now_str,
                    stage="CASE_MEMORY",
                    title="Historical Case Memory Retrieved",
                    description=f"Matched {len(case.similar_past_cases)} past cases via Cosine similarity (Top: {case.similar_past_cases[0]['title']}).",
                    actor="Case Memory Store",
                    status="INFO",
                )
            )

        timeline_events.append(
            TimelineEvent(
                timestamp=now_str,
                stage="MILESTONE_A",
                title=f"Pre-Evidence Action: {nba_pre.primary_action.value}",
                description=f"Route: {nba_pre.approval_route.value}. Rationale: {nba_pre.defensibility_rationale}",
                actor="Next Best Action Engine",
                status="WARNING" if "BLOCK" in nba_pre.primary_action.value else "INFO",
            )
        )

        timeline_events.append(
            TimelineEvent(
                timestamp=now_str,
                stage="STEP_UP_CHALLENGE",
                title=f"Step-Up Challenge: {chosen_step_up_status}",
                description=f"Challenge type: {case.step_up.challenge_type if case.step_up else 'SMS_OTP'}. Outcome: {chosen_step_up_status}.",
                actor="Verification Gateway",
                status="SUCCESS" if chosen_step_up_status == "CONFIRMED_LEGITIMATE" else "ALERT",
            )
        )

        timeline_events.append(
            TimelineEvent(
                timestamp=now_str,
                stage="MILESTONE_B",
                title=f"Post-Evidence Action: {nba_post.primary_action.value}",
                description=f"Route: {nba_post.approval_route.value}. Final Case Status: {case.status.value}.",
                actor="Reasoning Orchestrator",
                status="ALERT" if "BLOCK" in nba_post.primary_action.value else "SUCCESS",
            )
        )

        if case.sar and case.sar.filing_required:
            timeline_events.append(
                TimelineEvent(
                    timestamp=now_str,
                    stage="REGULATORY_FILING",
                    title=f"FinCEN SAR Generated: {case.sar.sar_id}",
                    description=f"Mandatory filing triggered for amount ${tx_signals.get('amount', 0.0):,.2f}.",
                    actor="Compliance Engine",
                    status="WARNING",
                )
            )

        timeline_events.append(
            TimelineEvent(
                timestamp=now_str,
                stage="GRAPH_WRITE_BACK",
                title="Graph Memory Persisted",
                description=f"Case vertex {case_id} and resolution committed to TigerGraph.",
                actor="TigerGraph Gateway",
                status="SUCCESS",
            )
        )

        case.timeline = timeline_events
        return case
