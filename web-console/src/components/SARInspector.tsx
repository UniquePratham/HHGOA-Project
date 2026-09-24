"use client";

import React, { useState } from "react";

export interface SARData {
  sar_id: string;
  filing_required: boolean;
  filing_reason: string;
  fin_cen_category: string;
  narrative: string;
  primary_subjects: string[];
  suspect_transactions: string[];
  total_dollar_amount: number;
  generated_at: string;
  compliance_signoff_needed: boolean;
}

export default function SARInspector({ sar }: { sar?: SARData | null }) {
  const [copied, setCopied] = useState(false);

  if (!sar || !sar.filing_required) {
    return null;
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(sar.narrative);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(sar, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${sar.sar_id}_fincen_filing.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="border border-[#262c37] p-5 bg-[#171b22] text-slate-100">
      <div className="flex justify-between items-baseline mb-3 pb-2 border-b border-[#262c37]">
        <h3 className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          FinCEN Suspicious Activity Report (SAR)
        </h3>
        <div className="flex gap-3 text-xs">
          <button onClick={handleCopy} className="text-sky-400 underline underline-offset-2 hover:text-sky-300 font-mono">
            {copied ? "Copied!" : "Copy Narrative"}
          </button>
          <button onClick={handleDownload} className="text-sky-400 underline underline-offset-2 hover:text-sky-300 font-mono">
            Export JSON
          </button>
        </div>
      </div>

      <div className="flex justify-between text-xs text-slate-400 mb-3 pb-2 border-b border-[#1c212a]">
        <span>Category: <strong className="font-mono text-slate-200">{sar.fin_cen_category}</strong></span>
        <span>Total Value: <strong className="font-mono text-slate-200">${(sar.total_dollar_amount || 0).toLocaleString()}</strong></span>
        <span>Subjects: <strong className="font-mono text-slate-200">{sar.primary_subjects.join(", ") || "N/A"}</strong></span>
      </div>

      <pre className="font-mono text-xs text-slate-300 bg-[#101318] p-4 border border-[#1c212a] max-h-48 overflow-y-auto whitespace-pre-wrap leading-relaxed">
        {sar.narrative}
      </pre>
    </div>
  );
}
