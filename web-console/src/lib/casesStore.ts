import casesData from "@/data/cases_store.json";
import benchmarkData from "@/data/benchmark_summary.json";

// In-memory working copy
let casesStore: any[] = JSON.parse(JSON.stringify(casesData));

export function getCases(): any[] {
  return casesStore;
}

export function getCaseById(caseId: string): any | undefined {
  return casesStore.find(
    (c) => c.case_id.toLowerCase() === caseId.toLowerCase()
  );
}

export function getBenchmarkSummary(): any {
  return benchmarkData;
}

export function updateCaseStepUp(
  caseId: string,
  responseStatus: string,
  notes?: string
): any | undefined {
  const c = getCaseById(caseId);
  if (!c) return undefined;

  const now = new Date().toISOString();

  // Update step-up record
  c.step_up = {
    method: "SMS_OTP",
    triggered_at: now,
    response_status: responseStatus,
    latency_seconds: 3.5,
    notes: notes || `Customer simulation: ${responseStatus}`,
  };

  // Adjust NBA and case status based on verification outcome
  if (responseStatus === "CONFIRMED_LEGITIMATE") {
    c.status = "RESOLVED_CLEARED";
    c.nba_post_evidence = {
      action: "ALLOW_TRANSACTION",
      primary_action: "ALLOW_TRANSACTION",
      risk_tier: "LOW",
      defensibility_score: 95.0,
      human_review_required: false,
      reasoning: "Step-up authentication confirmed legitimate cardholder authorization. Cleared for processing.",
      customer_interventions: ["RELEASE_FUNDS_HOLD", "RESTORE_CARD_ACTIVE_STATUS"],
      secondary_actions: ["LOG_CUSTOMER_DISPOSITION_IN_CASE_MANAGEMENT"],
    };
    c.sar = null;
    c.timeline.push({
      timestamp: now,
      phase: "RESOLUTION",
      description: `Step-up authentication passed: ${responseStatus}. Transaction allowed and hold released.`,
      actor: "AGENT_AUTOMATION",
      action_taken: "ALLOW_TRANSACTION",
      artifacts_generated: ["CLEARANCE_RECEIPT"],
    });
  } else {
    c.status = "RESOLVED_CONFIRMED_FRAUD";
    c.nba_post_evidence = {
      action: "BLOCK_TRANSACTION",
      primary_action: "BLOCK_TRANSACTION",
      risk_tier: "CRITICAL",
      defensibility_score: 99.0,
      human_review_required: true,
      reasoning: `Step-up challenge outcome (${responseStatus}) confirms unauthorized fraudulent activity. Permanent block and SAR filed.`,
      customer_interventions: ["BLOCK_CARD", "FREEZE_ACCOUNT", "SEND_FRAUD_ALERT_NOTIFICATION"],
      secondary_actions: ["FILE_FINCEN_SAR", "CLUSTER_ASSOCIATED_DEVICE_NODES_IN_GRAPH"],
    };
    c.timeline.push({
      timestamp: now,
      phase: "RESOLUTION",
      description: `Step-up challenge failed/confirmed fraud (${responseStatus}). Case escalated, transaction blocked, SAR submitted.`,
      actor: "AGENT_AUTOMATION",
      action_taken: "BLOCK_TRANSACTION",
      artifacts_generated: ["SAR_FILING_NARRATIVE", "BLOCK_CONFIRMATION"],
    });
  }

  return c;
}

export function searchCases(query: string): any {
  const cleanQ = query.trim().toUpperCase();
  const matched = casesStore.filter((c) => {
    return (
      c.case_id.toUpperCase().includes(cleanQ) ||
      c.subject_user_id.toUpperCase().includes(cleanQ) ||
      (c.subject_card_id && c.subject_card_id.toUpperCase().includes(cleanQ)) ||
      (c.suspect_transaction_ids &&
        c.suspect_transaction_ids.some((tx: string) =>
          tx.toUpperCase().includes(cleanQ)
        ))
    );
  });

  return {
    query,
    total_matches: matched.length,
    cases: matched.map((c) => ({
      case_id: c.case_id,
      title: c.title,
      status: c.status,
      risk_score: c.trigger?.initial_score || 0,
      user_id: c.subject_user_id,
    })),
  };
}
