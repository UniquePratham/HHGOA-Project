from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure agent-core is on sys.path
agent_core_dir = Path(__file__).resolve().parent.parent
if str(agent_core_dir) not in sys.path:
    sys.path.insert(0, str(agent_core_dir))

from agent.investigator import InvestigationOrchestrator
from benchmark.cases_dataset import BENCHMARK_20_CASES
from benchmark.evaluator import BenchmarkEvaluator
from graph.gateway import TigerGraphGateway


def run_all_benchmarks(output_dir: Path, verify_schema: bool = True) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    gateway = TigerGraphGateway(mode="fixture")
    orchestrator = InvestigationOrchestrator(gateway=gateway)

    print("=" * 80)
    print("RUNNING TIGERGRAPH AGENTIC FRAUD BENCHMARK EVALUATION (20 CASES)")
    print("=" * 80)

    summary_records = []
    
    for spec in BENCHMARK_20_CASES:
        # Run autonomous investigation
        case = orchestrator.run_full_investigation(
            transaction_id=spec.transaction_id,
            initial_risk=spec.upstream_model_risk,
            simulate_step_up_response=spec.simulated_step_up_response,
        )

        answer_file = BenchmarkEvaluator.build_answer_file(spec, case)
        answer_json = answer_file.model_dump_json(indent=2)

        out_file = output_dir / f"HHG-{spec.benchmark_id:03d}.json"
        out_file.write_text(answer_json, encoding="utf-8")

        summary_records.append({
            "benchmark_id": spec.benchmark_id,
            "case_id": case.case_id,
            "amount": spec.amount,
            "typology": spec.expected_typology,
            "nba_before_evidence": answer_file.next_best_action_before_additional_evidence.action,
            "step_up_result": spec.simulated_step_up_response,
            "nba_after_evidence": answer_file.next_best_action_after_additional_evidence.action,
            "approval_route": answer_file.next_best_action_after_additional_evidence.approval_route.required_route,
            "sar_filed": answer_file.suspicious_activity_report is not None,
            "graph_written": answer_file.written_to_graph,
        })

        print(
            f"Case {spec.benchmark_id:02d}: {spec.case_id} | ${spec.amount:>8.2f} | "
            f"Pre: {answer_file.next_best_action_before_additional_evidence.action:<22} | "
            f"Step-Up: {spec.simulated_step_up_response:<22} | "
            f"Post: {answer_file.next_best_action_after_additional_evidence.action:<18} | "
            f"SAR: {'YES' if answer_file.suspicious_activity_report else 'NO '}"
        )

    # Save summary manifest
    summary_path = output_dir / "benchmark_summary.json"
    summary_path.write_text(json.dumps(summary_records, indent=2), encoding="utf-8")

    print("=" * 80)
    print(f"SUCCESS: All 20 benchmark answer files generated in {output_dir}")
    print(f"Summary manifest saved to {summary_path}")
    print("=" * 80)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run 20 Benchmark Fraud Evaluation Cases")
    parser.add_argument("--output-dir", default="cases", help="Directory to save answer files")
    parser.add_argument("--verify-schema", action="store_true", default=True, help="Validate against answer schema")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    out_dir = (repo_root / args.output_dir).resolve()
    return run_all_benchmarks(out_dir, verify_schema=args.verify_schema)


if __name__ == "__main__":
    raise SystemExit(main())
