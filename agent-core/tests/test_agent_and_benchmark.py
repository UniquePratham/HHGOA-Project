import pytest
from agent.investigator import InvestigationOrchestrator
from agent.uncertainty import UncertaintyEngine
from benchmark.cases_dataset import BENCHMARK_20_CASES
from benchmark.evaluator import BenchmarkEvaluator
from graph.gateway import TigerGraphGateway


def test_investigator_end_to_end():
    gateway = TigerGraphGateway(mode="fixture")
    orchestrator = InvestigationOrchestrator(gateway=gateway)

    case = orchestrator.run_full_investigation("TX_RING_103", initial_risk=92.0)
    assert case.status.value in ["RESOLVED_CONFIRMED_FRAUD", "RESOLVED_CLEARED"]
    assert case.nba_pre_evidence is not None
    assert case.nba_post_evidence is not None
    assert case.graph_write_back_status == "COMMITTED"
    assert len(case.evidence) >= 2


def test_uncertainty_thresholds():
    # Ambiguous signals without step-up
    signals = {"device_id": "DEV_01", "ip_id": "IP_01"}
    unc = UncertaintyEngine.assess_uncertainty(initial_risk=65.0, graph_signals=signals, step_up_completed=False)
    assert unc.requires_step_up is True
    assert unc.can_defensively_act is False

    # Step-up completed
    unc_post = UncertaintyEngine.assess_uncertainty(initial_risk=65.0, graph_signals=signals, step_up_completed=True, step_up_status="CONFIRMED_LEGITIMATE")
    assert unc_post.can_defensively_act is True
    assert unc_post.risk_score <= 30.0


def test_benchmark_answer_file_generation():
    gateway = TigerGraphGateway(mode="fixture")
    orchestrator = InvestigationOrchestrator(gateway=gateway)
    spec = BENCHMARK_20_CASES[0]

    case = orchestrator.run_full_investigation(spec.transaction_id, initial_risk=spec.upstream_model_risk)
    ans = BenchmarkEvaluator.build_answer_file(spec, case)

    assert ans.benchmark_id == 1
    assert ans.written_to_graph is True
    assert ans.next_best_action_before_additional_evidence.action != ""
    assert ans.next_best_action_after_additional_evidence.action != ""
    assert len(ans.findings) > 0
