import pytest
from starlette.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["active_cases"] >= 4


def test_list_and_get_case():
    res = client.get("/api/cases")
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) >= 4
    case_id = cases[0]["case_id"]

    res_single = client.get(f"/api/cases/{case_id}")
    assert res_single.status_code == 200
    single_data = res_single.json()
    assert single_data["case_id"] == case_id
    assert "nba_pre_evidence" in single_data
    assert "nba_post_evidence" in single_data


def test_investigate_endpoint():
    payload = {
        "transaction_id": "TX_SAFE_101",
        "initial_risk": 15.0,
    }
    res = client.post("/api/investigate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["case_id"] == "CASE-TX_SAFE_101"
    assert data["status"] == "RESOLVED_CLEARED"


def test_step_up_endpoint():
    res_list = client.get("/api/cases")
    case_id = res_list.json()[0]["case_id"]

    payload = {
        "response_status": "CONFIRMED_LEGITIMATE",
        "notes": "Analyst verified via direct telephone callback",
    }
    res = client.post(f"/api/cases/{case_id}/step-up", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["step_up"]["response_status"] == "CONFIRMED_LEGITIMATE"
    assert data["nba_post_evidence"]["primary_action"] == "ALLOW_TRANSACTION"


def test_benchmark_summary_endpoint():
    res = client.get("/api/benchmark/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_evaluated"] == 20
    assert data["sar_filings_count"] > 0


def test_search_endpoint():
    res = client.get("/api/search?q=RING")
    assert res.status_code == 200
    data = res.json()
    assert data["total_matches"] > 0
    assert len(data["cases"]) > 0 or len(data["devices"]) > 0


def test_print_endpoint():
    res_list = client.get("/api/cases")
    case_id = res_list.json()[0]["case_id"]

    res_print = client.get(f"/api/cases/{case_id}/print")
    assert res_print.status_code == 200
    data = res_print.json()
    assert data["case_id"] == case_id
    assert "report_title" in data
    assert "timeline" in data
    assert len(data["timeline"]) > 0
