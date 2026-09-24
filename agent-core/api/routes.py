from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from agent.investigator import InvestigationOrchestrator
from benchmark.cases_dataset import BENCHMARK_20_CASES
from benchmark.evaluator import BenchmarkEvaluator
from graph.gateway import TigerGraphGateway
from models.case import FraudCase

router = APIRouter()
gateway = TigerGraphGateway(mode="fixture")
orchestrator = InvestigationOrchestrator(gateway=gateway)

# In-memory case cache
CASES_STORE: Dict[str, FraudCase] = {}

# Seed investigations on startup (including benchmark test cases)
for spec in BENCHMARK_20_CASES:
    init_case = orchestrator.run_full_investigation(
        spec.transaction_id,
        initial_risk=spec.upstream_model_risk,
        simulate_step_up_response=spec.simulated_step_up_response,
    )
    CASES_STORE[init_case.case_id] = init_case



class InvestigateRequest(BaseModel):
    transaction_id: str
    initial_risk: Optional[float] = None
    simulate_step_up_response: Optional[str] = None


class StepUpSubmission(BaseModel):
    response_status: str  # "CONFIRMED_LEGITIMATE", "CONFIRMED_FRAUD", "FAILED_VERIFICATION", "TIMEOUT_NO_RESPONSE"
    notes: Optional[str] = None


@router.get("/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "TigerGraph Agentic Fraud Investigation API",
        "gateway_mode": gateway.mode,
        "active_cases": len(CASES_STORE),
    }


@router.post("/investigate", response_model=FraudCase)
def investigate_transaction(req: InvestigateRequest) -> FraudCase:
    case = orchestrator.run_full_investigation(
        transaction_id=req.transaction_id,
        initial_risk=req.initial_risk,
        simulate_step_up_response=req.simulate_step_up_response,
    )
    CASES_STORE[case.case_id] = case
    return case


@router.get("/cases", response_model=List[FraudCase])
def list_cases() -> List[FraudCase]:
    return list(CASES_STORE.values())


@router.get("/cases/{case_id}", response_model=FraudCase)
def get_case(case_id: str) -> FraudCase:
    if case_id not in CASES_STORE:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return CASES_STORE[case_id]


@router.post("/cases/{case_id}/step-up", response_model=FraudCase)
def submit_step_up_response(case_id: str, sub: StepUpSubmission) -> FraudCase:
    if case_id not in CASES_STORE:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    
    existing = CASES_STORE[case_id]
    tx_id = existing.suspect_transaction_ids[0] if existing.suspect_transaction_ids else "TX_UNKNOWN"
    
    # Re-run investigation with specific customer response
    updated_case = orchestrator.run_full_investigation(
        transaction_id=tx_id,
        initial_risk=existing.trigger.initial_score,
        simulate_step_up_response=sub.response_status,
    )
    if sub.notes and updated_case.step_up:
        updated_case.step_up.notes = sub.notes

    CASES_STORE[case_id] = updated_case
    return updated_case


@router.get("/graph/{node_id}/ego")
def get_ego_network(node_id: str, radius: int = Query(2, ge=1, le=3)) -> Dict[str, Any]:
    ego = gateway.get_ego_graph(node_id, radius=radius)
    return ego.model_dump()


@router.get("/benchmark/cases")
def get_benchmark_cases() -> List[Dict[str, Any]]:
    return [c.model_dump() for c in BENCHMARK_20_CASES]


@router.get("/benchmark/summary")
def get_benchmark_summary() -> Dict[str, Any]:
    results = []
    for spec in BENCHMARK_20_CASES:
        case = orchestrator.run_full_investigation(
            spec.transaction_id,
            initial_risk=spec.upstream_model_risk,
            simulate_step_up_response=spec.simulated_step_up_response,
        )
        ans = BenchmarkEvaluator.build_answer_file(spec, case)
        results.append({
            "benchmark_id": spec.benchmark_id,
            "case_id": case.case_id,
            "amount": spec.amount,
            "typology": spec.expected_typology,
            "action_pre": ans.next_best_action_before_additional_evidence.action,
            "step_up": spec.simulated_step_up_response,
            "action_post": ans.next_best_action_after_additional_evidence.action,
            "sar_filed": ans.suspicious_activity_report is not None,
        })
    return {
        "total_evaluated": len(results),
        "sar_filings_count": sum(1 for r in results if r["sar_filed"]),
        "blocks_count": sum(1 for r in results if r["action_post"] == "BLOCK_TRANSACTION"),
        "cleared_count": sum(1 for r in results if r["action_post"] == "ALLOW_TRANSACTION"),
        "results": results,
    }


@router.get("/search")
def search_entities(q: str = Query(..., min_length=1, max_length=100)) -> Dict[str, Any]:
    """
    Multi-entity global search across cases, transactions, accounts, devices, and IPs.
    """
    clean_q = q.strip().upper()
    matched_cases = []
    for c_id, c in CASES_STORE.items():
        if (clean_q in c_id.upper() or
            clean_q in c.subject_user_id.upper() or
            (c.subject_card_id and clean_q in c.subject_card_id.upper()) or
            any(clean_q in tx.upper() for tx in c.suspect_transaction_ids)):
            matched_cases.append({
                "case_id": c.case_id,
                "title": c.title,
                "status": c.status.value,
                "risk_score": c.trigger.initial_score,
                "user_id": c.subject_user_id,
            })

    # Search in graph topology
    graph_matches = {"transactions": [], "users": [], "devices": [], "ips": []}
    for node_id, attrs in gateway._graph.nodes(data=True):
        if clean_q in str(node_id).upper() or clean_q in str(attrs.get("label", "")).upper():
            e_type = attrs.get("entity_type", "")
            item = {"id": node_id, "label": attrs.get("label", node_id), "type": e_type, "properties": attrs}
            if e_type == "Transaction":
                graph_matches["transactions"].append(item)
            elif e_type == "User" or e_type == "Account":
                graph_matches["users"].append(item)
            elif e_type == "Device":
                graph_matches["devices"].append(item)
            elif e_type == "IP":
                graph_matches["ips"].append(item)

    return {
        "query": q,
        "total_matches": len(matched_cases) + sum(len(v) for v in graph_matches.values()),
        "cases": matched_cases,
        **graph_matches,
    }


@router.get("/cases/{case_id}/print")
def get_printable_case_report(case_id: str) -> Dict[str, Any]:
    """
    Structured data payload formatted specifically for printable executive dossier reports.
    """
    if case_id not in CASES_STORE:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    case = CASES_STORE[case_id]
    
    return {
        "report_title": f"Financial Crimes Investigation Report - {case.case_id}",
        "generated_timestamp": case.updated_at,
        "case_id": case.case_id,
        "status": case.status.value,
        "subject_user": case.subject_user_id,
        "subject_card": case.subject_card_id,
        "suspect_transactions": case.suspect_transaction_ids,
        "trigger": case.trigger.model_dump(),
        "risk_assessment": {
            "initial_score": case.trigger.initial_score,
            "final_risk": case.uncertainty_post_evidence.risk_score if case.uncertainty_post_evidence else case.trigger.initial_score,
            "completeness_ici": case.uncertainty_pre_evidence.information_completeness_index if case.uncertainty_pre_evidence else 0.6,
            "confidence": case.uncertainty_post_evidence.confidence if case.uncertainty_post_evidence else 0.8,
        },
        "timeline": [t.model_dump() for t in case.timeline],
        "evidence_facts": [e.model_dump() for e in case.evidence if e.type.value == "OBSERVED_FACT"],
        "evidence_inferences": [e.model_dump() for e in case.evidence if e.type.value == "INFERENCE"],
        "next_best_actions": {
            "milestone_a_pre_evidence": case.nba_pre_evidence.model_dump() if case.nba_pre_evidence else None,
            "milestone_b_post_evidence": case.nba_post_evidence.model_dump() if case.nba_post_evidence else None,
        },
        "suspicious_activity_report": case.sar.model_dump() if case.sar else None,
        "graph_provenance": {
            "target_graph": "FraudGraph",
            "write_back_status": case.graph_write_back_status,
            "node_count": len(case.ego_graph.nodes) if case.ego_graph else 0,
            "edge_count": len(case.ego_graph.edges) if case.ego_graph else 0,
        },
    }
