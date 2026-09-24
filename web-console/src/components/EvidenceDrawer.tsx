"use client";

import React from "react";

export interface EvidenceItem {
  id: string;
  type: string;
  severity: string;
  title: string;
  description: string;
  source: string;
  confidence: number;
  related_entity_id?: string;
}

interface EvidenceDrawerProps {
  evidence: EvidenceItem[];
  onHighlightEntity?: (entityId: string) => void;
}

export default function EvidenceDrawer({
  evidence,
  onHighlightEntity,
}: EvidenceDrawerProps) {
  return (
    <div className="flex flex-col">
      <div className="flex justify-between items-baseline mb-2 pb-1 border-b border-[#1c212a]">
        <h2 className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Structured Evidence Record
        </h2>
        <span className="text-[11px] text-slate-500 font-mono">
          {evidence.length} signals logged
        </span>
      </div>

      <div className="divide-y divide-[#1c212a]">
        {evidence.map((item, idx) => {
          const isFact = item.type === "OBSERVED_FACT";
          const isInfer = item.type === "INFERENCE";
          const tagColor = isFact
            ? "text-emerald-500"
            : isInfer
            ? "text-sky-400"
            : "text-amber-400";
          const numStr = (idx + 1 < 10 ? "0" : "") + (idx + 1);

          return (
            <div key={item.id} className="py-3 grid grid-cols-[28px_1fr_auto] gap-3 items-start">
              <span className="font-mono text-xs text-slate-500 font-semibold">{numStr}</span>
              
              <div className="flex flex-col gap-0.5">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-bold uppercase tracking-wider ${tagColor}`}>
                    {item.type.replace(/_/g, " ")}
                  </span>
                  <strong className="text-xs font-semibold text-slate-100">{item.title}</strong>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{item.description}</p>
                <div className="flex gap-4 text-[11px] text-slate-500 mt-1">
                  <span>Source: <span className="font-mono text-slate-400">{item.source}</span></span>
                  <span>Confidence: <strong className="font-mono text-slate-300">{(item.confidence * 100).toFixed(0)}%</strong></span>
                </div>
              </div>

              <div>
                {item.related_entity_id && onHighlightEntity && (
                  <button
                    onClick={() => onHighlightEntity(item.related_entity_id!)}
                    className="text-[11px] text-sky-400 underline underline-offset-2 hover:text-sky-300 font-mono"
                  >
                    View in Graph
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
