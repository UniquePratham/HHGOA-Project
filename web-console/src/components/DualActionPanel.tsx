"use client";

import React from "react";

export interface NextBestActionItem {
  milestone: string;
  primary_action: string;
  secondary_actions: string[];
  approval_route: string;
  defensibility_rationale: string;
  policy_citation: string;
  requires_human_signoff: boolean;
}

interface DualActionPanelProps {
  nbaPost?: NextBestActionItem;
  onOpenStepUp?: () => void;
  onApprove?: () => void;
  onReject?: () => void;
}

export default function DualActionPanel({
  nbaPost,
  onOpenStepUp,
  onApprove,
  onReject,
}: DualActionPanelProps) {
  return (
    <div className="border-2 border-[#262c37] p-5 bg-[#171b22] text-slate-100 mb-6">
      <div className="flex justify-between items-baseline border-b border-[#262c37] pb-3 mb-3">
        <div>
          <div className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
            Milestone B · Post-Evidence Recommendation
          </div>
          <div className="text-lg font-bold font-mono text-slate-100 tracking-tight mt-0.5">
            {nbaPost?.primary_action || "EVALUATING DEFENSIVE ACTION..."}
          </div>
        </div>
        <span className="text-[10px] font-bold tracking-wider px-2 py-0.5 bg-amber-950/60 text-amber-400 border border-amber-800 rounded">
          SIMULATED ACTION
        </span>
      </div>

      <div className="text-xs text-slate-300 mb-2">
        Rationale based on graph topology, historical case memory, and bank policy:
      </div>

      <ul className="list-disc list-inside space-y-1 text-xs text-slate-400 mb-4 pl-1">
        {nbaPost?.secondary_actions && nbaPost.secondary_actions.length > 0 ? (
          nbaPost.secondary_actions.map((act, i) => <li key={i}>{act}</li>)
        ) : (
          <li>
            {nbaPost?.defensibility_rationale ||
              "Multi-hop community detection and risk scoring indicate high probability of syndicate activity."}
          </li>
        )}
      </ul>

      <div className="flex justify-between text-xs text-slate-400 border-t border-[#262c37] pt-3">
        <div>
          Policy Citation: <strong className="font-mono text-slate-200">{nbaPost?.policy_citation || "FIM-POL-04"}</strong>
        </div>
        <div>
          Approval Route: <strong className="font-mono text-slate-200">{nbaPost?.approval_route || "COMPLIANCE_DIRECTOR"}</strong>
        </div>
      </div>

      <div className="flex flex-wrap gap-2.5 mt-4 pt-3 border-t border-[#262c37]">
        <button
          onClick={onOpenStepUp}
          className="bg-red-700 hover:bg-red-600 text-white text-xs font-semibold px-4 py-2 rounded transition"
        >
          Inject Step-Up Verification
        </button>
        <button
          onClick={onApprove}
          className="bg-[#1f242e] hover:bg-[#262c37] border border-[#262c37] text-slate-200 text-xs font-medium px-4 py-2 rounded transition"
        >
          Approve Action
        </button>
        <button
          onClick={onReject}
          className="bg-[#1f242e] hover:bg-[#262c37] border border-[#262c37] text-slate-200 text-xs font-medium px-4 py-2 rounded transition"
        >
          Reject Action
        </button>
      </div>
    </div>
  );
}
