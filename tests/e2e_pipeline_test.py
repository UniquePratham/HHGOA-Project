import json
from pathlib import Path
import pytest
from starlette.testclient import TestClient

from agent.investigator import InvestigationOrchestrator
from api.app import app
from benchmark.cases_dataset import BENCHMARK_20_CASES
from graph.gateway import TigerGraphGateway

client = TestClient(app)


def test_full_pipeline_end_to_end():
    # 1. Trigger an investigation on high-risk syndicate transaction
    res = client.post("/api/investigate", json={"transaction_id": "TX_RING_103", "initial_risk": 92.0})
    assert res.status_code == 200
    case = res.json()
    case_id = case["case_id"]

    # 2. Verify graph ego-net returned
    assert case["ego_graph"] is not None
    assert len(case["ego_graph"]["nodes"]) > 0

    # 3. Verify Milestone A NBA
    assert case["nba_pre_evidence"] is not None
    assert case["nba_pre_evidence"]["primary_action"] == "BLOCK_TRANSACTION"

    # 4. Verify Step-Up simulation
    res_step = client.post(f"/api/cases/{case_id}/step-up", json={
        "response_status": "CONFIRMED_FRAUD",
        "notes": "Cardholder confirmed unauthorized activity",
    })
    assert res_step.status_code == 200
    updated_case = res_step.json()
    assert updated_case["status"] == "RESOLVED_CONFIRMED_FRAUD"

    # 5. Verify Milestone B NBA & SAR
    assert updated_case["nba_post_evidence"]["primary_action"] == "BLOCK_TRANSACTION"
    assert updated_case["sar"] is not None
    assert updated_case["sar"]["filing_required"] is True
    assert "SUSPICIOUS ACTIVITY REPORT" in updated_case["sar"]["narrative"]


def test_benchmark_files_integrity():
    repo_root = Path(__file__).resolve().parent.parent
    answers_dir = repo_root / "artifacts" / "benchmark_answers"
    assert answers_dir.exists()

    summary_file = answers_dir / "benchmark_summary.json"
    assert summary_file.exists()

    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)

    assert len(summary) == 20

    # Verify all 20 individual case files exist and match schema
    for i in range(1, 21):
        case_file = answers_dir / f"case_{i:02d}.json"
        assert case_file.exists()
        with open(case_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["benchmark_id"] == i
            assert "next_best_action_before_additional_evidence" in data
            assert "next_best_action_after_additional_evidence" in data
            assert data["written_to_graph"] is True
