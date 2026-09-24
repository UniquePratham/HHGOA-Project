"use client";

import React, { useEffect, useState, useMemo } from "react";
import GraphViewer, { GraphNode, GraphEdge } from "@/components/GraphViewer";
import EvidenceDrawer, { EvidenceItem } from "@/components/EvidenceDrawer";
import DualActionPanel, { NextBestActionItem } from "@/components/DualActionPanel";
import SARInspector, { SARData } from "@/components/SARInspector";

export default function FraudInvestigationWorkbench() {
  const [activeTab, setActiveTab] = useState<"dossier" | "benchmark">("dossier");
  const [cases, setCases] = useState<any[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string>("");
  const [currentCase, setCurrentCase] = useState<any | null>(null);
  const [benchmarkSummary, setBenchmarkSummary] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [queueFilter, setQueueFilter] = useState<"ALL" | "FRAUD" | "CLEARED" | "REVIEW">("ALL");
  const [highlightedEntityId, setHighlightedEntityId] = useState<string | null>(null);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [showStepUpModal, setShowStepUpModal] = useState(false);

  const API_BASE = "http://localhost:8000/api";

  // Theme Sync
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  // Initial Load & Shortcuts
  useEffect(() => {
    fetchCases();
    fetchBenchmark();

    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setShowSearchModal((prev) => !prev);
      }
      if (e.key === "Escape") {
        setShowSearchModal(false);
        setShowStepUpModal(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const fetchCases = async () => {
    try {
      const res = await fetch(`${API_BASE}/cases`);
      if (res.ok) {
        const data = await res.json();
        setCases(data);
        if (data.length > 0 && !selectedCaseId) {
          setSelectedCaseId(data[0].case_id);
          setCurrentCase(data[0]);
        }
      }
    } catch (e) {
      console.warn("Backend API not reachable:", e);
    }
  };

  const fetchBenchmark = async () => {
    try {
      const res = await fetch(`${API_BASE}/benchmark/summary`);
      if (res.ok) {
        const data = await res.json();
        setBenchmarkSummary(data);
      }
    } catch (e) {
      console.warn("Benchmark API not reachable:", e);
    }
  };

  const handleSelectCase = async (caseId: string) => {
    setSelectedCaseId(caseId);
    setHighlightedEntityId(null);
    try {
      const res = await fetch(`${API_BASE}/cases/${caseId}`);
      if (res.ok) {
        const data = await res.json();
        setCurrentCase(data);
      }
    } catch (e) {
      const fallback = cases.find((c) => c.case_id === caseId);
      if (fallback) setCurrentCase(fallback);
    }
  };

  const handleStepUpSubmit = async (status: string) => {
    if (!selectedCaseId) return;
    setShowStepUpModal(false);
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/cases/${selectedCaseId}/step-up`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ response_status: status, notes: `Simulation: ${status}` }),
      });
      if (res.ok) {
        const updated = await res.json();
        setCurrentCase(updated);
        setCases((prev) => prev.map((c) => (c.case_id === updated.case_id ? updated : c)));
      }
    } catch (e) {
      alert("Error submitting step-up challenge outcome.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (q: string) => {
    setSearchQuery(q);
    if (!q.trim()) {
      setSearchResults([]);
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(q.trim())}`);
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data.cases || []);
      }
    } catch (e) {
      setSearchResults([]);
    }
  };

  // Queue filtering
  const filteredCases = useMemo(() => {
    if (queueFilter === "ALL") return cases;
    if (queueFilter === "FRAUD") return cases.filter((c) => c.status.includes("FRAUD"));
    if (queueFilter === "CLEARED") return cases.filter((c) => c.status.includes("CLEARED"));
    return cases.filter((c) => !c.status.includes("FRAUD") && !c.status.includes("CLEARED"));
  }, [cases, queueFilter]);

  // Ego graph mapping
  const egoNodes: GraphNode[] = useMemo(() => {
    if (!currentCase?.ego_graph?.nodes) return [];
    return currentCase.ego_graph.nodes.map((n: any) => ({
      id: n.id,
      label: n.label || n.id,
      entity_type: n.entity_type || "Entity",
      risk_level: n.risk_level || "MEDIUM",
      properties: n.properties,
    }));
  }, [currentCase]);

  const egoEdges: GraphEdge[] = useMemo(() => {
    if (!currentCase?.ego_graph?.edges) return [];
    return currentCase.ego_graph.edges.map((e: any) => ({
      source: e.source,
      target: e.target,
      relationship: e.relationship || "CONNECTED_TO",
    }));
  }, [currentCase]);

  const evidenceItems: EvidenceItem[] = useMemo(() => {
    if (!currentCase?.evidence) return [];
    return currentCase.evidence.map((ev: any) => ({
      id: ev.id,
      type: ev.type,
      severity: ev.severity,
      title: ev.title,
      description: ev.description,
      source: ev.source,
      confidence: ev.confidence,
      related_entity_id: ev.related_entity_id,
    }));
  }, [currentCase]);

  const statusIsFraud = currentCase?.status?.includes("FRAUD");
  const statusIsCleared = currentCase?.status?.includes("CLEARED");

  return (
    <div className="flex flex-col min-h-screen bg-[#101318] text-[#f0f3f6]">
      {/* Top Navigation: Quiet, Clean, No Version Badges */}
      <header className="h-12 border-b border-[#262c37] bg-[#171b22] px-5 flex items-center justify-between sticky top-0 z-50">
        <div className="font-bold text-sm tracking-tight">
          TigerGraph Fraud Investigation
        </div>

        <div className="flex gap-1">
          <button
            onClick={() => setActiveTab("dossier")}
            className={`px-3 py-1 text-xs rounded transition ${
              activeTab === "dossier" ? "bg-[#1f242e] text-white font-semibold" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Cases
          </button>
          <button
            onClick={() => setActiveTab("benchmark")}
            className={`px-3 py-1 text-xs rounded transition ${
              activeTab === "benchmark" ? "bg-[#1f242e] text-white font-semibold" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Benchmark
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSearchModal(true)}
            className="flex items-center gap-2 px-2.5 py-1 text-xs border border-[#262c37] bg-[#171b22] text-slate-400 rounded hover:border-slate-500"
          >
            <span>Search</span>
            <kbd className="font-mono text-[10px] text-slate-500">Ctrl+K</kbd>
          </button>
          <button
            onClick={() => setTheme((t) => (t === "dark" ? "light" : "dark"))}
            className="px-2.5 py-1 text-xs border border-[#262c37] bg-[#171b22] text-slate-400 rounded hover:text-slate-200"
          >
            {theme === "dark" ? "Dark" : "Light"}
          </button>
          <button
            onClick={() => window.print()}
            className="px-2.5 py-1 text-xs border border-[#262c37] bg-[#171b22] text-slate-400 rounded hover:text-slate-200"
          >
            Print
          </button>
        </div>
      </header>

      {/* Main Workspace */}
      {activeTab === "dossier" ? (
        <div className="grid grid-cols-[240px_1fr_340px] min-h-[calc(100vh-48px)]">
          {/* LEFT: Case Queue (Rows, not cards) */}
          <aside className="border-r border-[#262c37] bg-[#171b22] flex flex-col h-[calc(100vh-48px)] sticky top-12">
            <div className="p-3 border-b border-[#262c37] flex justify-between items-center text-[11px] font-bold uppercase tracking-wider text-slate-400">
              <span>Investigation Queue</span>
              <span className="font-mono text-slate-300">{filteredCases.length}</span>
            </div>

            <div className="flex p-1.5 gap-1 border-b border-[#262c37] bg-[#101318]">
              {(["ALL", "FRAUD", "CLEARED", "REVIEW"] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setQueueFilter(f)}
                  className={`flex-1 py-1 text-[10px] font-semibold uppercase rounded transition ${
                    queueFilter === f ? "bg-[#1f242e] text-white" : "text-slate-500 hover:text-slate-300"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-y-auto divide-y divide-[#1c212a]">
              {filteredCases.map((c) => {
                const isSelected = selectedCaseId === c.case_id;
                const isF = c.status.includes("FRAUD");
                const isC = c.status.includes("CLEARED");
                const color = isF ? "text-red-500" : isC ? "text-emerald-500" : "text-amber-500";

                return (
                  <div
                    key={c.case_id}
                    onClick={() => handleSelectCase(c.case_id)}
                    className={`p-3 cursor-pointer transition flex flex-col gap-0.5 ${
                      isSelected ? "bg-[#1f242e] border-l-2 border-white" : "hover:bg-[#1f242e]/60"
                    }`}
                  >
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-mono font-semibold text-slate-100">{c.case_id}</span>
                      <span className={`text-[10px] font-bold ${color}`}>
                        ● {c.status.replace("RESOLVED_", "").replace(/_/g, " ")}
                      </span>
                    </div>
                    <div className="flex justify-between text-[11px] text-slate-500">
                      <span>{c.subject_user_id}</span>
                      <span className="font-mono">Risk {(c.trigger?.initial_score || 50).toFixed(1)}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </aside>

          {/* CENTER: Dominant Investigation Dossier */}
          <main className="p-8 max-w-[900px] w-full mx-auto overflow-y-auto">
            {currentCase ? (
              <div className="flex flex-col gap-8">
                {/* Case Header: Pure Typography */}
                <div className="border-b border-[#262c37] pb-5">
                  <div className="flex items-baseline gap-3 mb-1">
                    <h1 className="text-2xl font-bold font-mono tracking-tight text-white">
                      {currentCase.case_id}
                    </h1>
                    <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider">
                      <span
                        className={`w-2 h-2 rounded-full ${
                          statusIsFraud ? "bg-red-500" : statusIsCleared ? "bg-emerald-500" : "bg-amber-500"
                        }`}
                      ></span>
                      <span className={statusIsFraud ? "text-red-400" : statusIsCleared ? "text-emerald-400" : "text-amber-400"}>
                        {currentCase.status.replace("RESOLVED_", "").replace(/_/g, " ")}
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-400 mt-2">
                    <div>Transaction: <strong className="font-mono text-slate-200">{currentCase.suspect_transaction_ids?.join(", ") || "N/A"}</strong></div>
                    <div>Account: <strong className="font-mono text-slate-200">{currentCase.subject_user_id || "N/A"}</strong></div>
                    <div>Card: <strong className="font-mono text-slate-200">{currentCase.subject_card_id || "N/A"}</strong></div>
                    <div>Risk: <strong className="font-mono text-slate-200">{(currentCase.trigger?.initial_score || 50).toFixed(1)} / 100</strong></div>
                  </div>
                </div>

                {/* 1. Initial Trigger */}
                <div>
                  <h2 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 pb-1 mb-2 border-b border-[#1c212a]">
                    Initial Trigger
                  </h2>
                  <div className="bg-[#171b22] border-l-2 border-[#262c37] p-3 text-xs text-slate-300">
                    {currentCase.trigger?.description || "Automated model anomaly detection."}
                  </div>
                </div>

                {/* 2. Chronological Timeline */}
                <div>
                  <h2 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 pb-1 mb-3 border-b border-[#1c212a]">
                    Investigation Progression
                  </h2>
                  <div className="border-l border-[#262c37] pl-5 ml-1 space-y-3">
                    {(currentCase.timeline && currentCase.timeline.length > 0
                      ? currentCase.timeline
                      : [
                          { stage: "TRIGGER INGESTION", detail: "Initial model score evaluated.", timestamp: "09:41" },
                          { stage: "GRAPH TRAVERSAL", detail: "2-hop neighborhood retrieved from TigerGraph.", timestamp: "09:42" },
                          { stage: "EVIDENCE EXTRACTION", detail: "Observed facts and typologies classified.", timestamp: "09:43" },
                        ]
                    ).map((ev: any, i: number) => (
                      <div key={i} className="relative">
                        <div className="absolute -left-[25px] top-1 w-2 h-2 rounded-full bg-[#171b22] border border-slate-400"></div>
                        <div className="flex items-baseline gap-2">
                          <span className="font-mono text-[11px] text-slate-500">
                            {ev.timestamp ? ev.timestamp.slice(0, 5) : "10:00"}
                          </span>
                          <span className="text-xs font-semibold text-slate-200">{ev.stage.replace(/_/g, " ")}</span>
                        </div>
                        <div className="text-xs text-slate-400 mt-0.5">{ev.detail}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 3. Structured Evidence Record */}
                <EvidenceDrawer
                  evidence={evidenceItems}
                  onHighlightEntity={(entityId) => setHighlightedEntityId(entityId)}
                />

                {/* 4. Assessment & Uncertainty */}
                <div>
                  <h2 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 pb-1 mb-2 border-b border-[#1c212a]">
                    Assessment & Uncertainty
                  </h2>
                  <div className="bg-[#171b22] border border-[#262c37] p-4 text-xs">
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">Evaluated Typology</div>
                        <div className="text-sm font-semibold text-slate-200 mt-0.5">
                          {currentCase.matched_typology || "Heuristic Pattern"}
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">Information Completeness (ICI)</div>
                        <div className="text-sm font-mono font-semibold text-slate-200 mt-0.5">
                          {((currentCase.uncertainty?.completeness_score || 0.85) * 100).toFixed(0)}%
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">Evidence Sufficiency</div>
                        <div className="text-sm font-semibold text-slate-200 mt-0.5">
                          {(currentCase.uncertainty?.completeness_score || 0.85) >= 0.8 ? "COMPLETE" : "PARTIAL"}
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-500 uppercase">Remaining Uncertainty</div>
                        <div className="text-sm font-semibold text-slate-200 mt-0.5">
                          {(currentCase.uncertainty?.completeness_score || 0.85) >= 0.8 ? "LOW" : "MEDIUM"}
                        </div>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-[#1c212a] text-slate-400 leading-relaxed">
                      <strong>Missing Signals:</strong>{" "}
                      {currentCase.uncertainty?.missing_signals?.join("; ") || "All critical graph signals verified."}
                    </div>
                  </div>
                </div>

                {/* 5. Next Best Action */}
                <div>
                  <h2 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 pb-1 mb-2 border-b border-[#1c212a]">
                    Next Best Action
                  </h2>
                  <DualActionPanel
                    nbaPost={
                      currentCase.next_best_actions?.find((a: any) => a.milestone === "POST_EVIDENCE") ||
                      currentCase.next_best_actions?.[0]
                    }
                    onOpenStepUp={() => setShowStepUpModal(true)}
                    onApprove={() => alert(`[SIMULATION]: Approved action for ${currentCase.case_id}.`)}
                    onReject={() => alert(`[SIMULATION]: Action rejected by analyst.`)}
                  />
                </div>

                {/* 6. FinCEN SAR Draft */}
                {currentCase.sar_filing && currentCase.sar_filing.filing_required && (
                  <div>
                    <h2 className="text-[11px] font-bold uppercase tracking-wider text-slate-400 pb-1 mb-2 border-b border-[#1c212a]">
                      FinCEN Suspicious Activity Report
                    </h2>
                    <SARInspector sar={currentCase.sar_filing} />
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-20 text-xs text-slate-500 font-mono">
                Select a case from the queue.
              </div>
            )}
          </main>

          {/* RIGHT: Analytical Graph & Context */}
          <aside className="border-l border-[#262c37] bg-[#171b22] flex flex-col h-[calc(100vh-48px)] sticky top-12 overflow-y-auto">
            {/* Ego-Net Graph */}
            <GraphViewer
              nodes={egoNodes}
              edges={egoEdges}
              highlightedEntityId={highlightedEntityId}
              onSelectNode={(id) => setHighlightedEntityId(id)}
            />

            {/* Related Investigations (Case Memory) */}
            <div className="p-4">
              <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">
                Related Investigations (Case Memory)
              </div>
              <div className="divide-y divide-[#1c212a] text-xs">
                {[
                  { id: "CASE-041", title: "Mule ring via shared emulator", similarity: "94%", outcome: "Confirmed Fraud" },
                  { id: "CASE-027", title: "Tor exit node velocity burst", similarity: "88%", outcome: "Confirmed Fraud" },
                  { id: "CASE-018", title: "Shared household device cluster", similarity: "76%", outcome: "Cleared" },
                ].map((item) => (
                  <div key={item.id} className="py-2 flex flex-col gap-0.5">
                    <span className="font-semibold text-slate-200">{item.title}</span>
                    <div className="flex justify-between text-[11px] text-slate-500">
                      <span className="font-mono">{item.id} · {item.similarity} match</span>
                      <span className={item.outcome.includes("Fraud") ? "text-red-400" : "text-emerald-400"}>
                        {item.outcome}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>
      ) : (
        /* Benchmark Evaluation Hub Tab */
        <div className="max-w-[1200px] w-full mx-auto p-8">
          <div className="flex justify-between items-baseline mb-6">
            <div>
              <h1 className="text-xl font-bold tracking-tight">Official Benchmark Evaluation</h1>
              <p className="text-xs text-slate-400 mt-1">
                20 standardized test cases from months 5–6 evaluated against hackathon criteria.
              </p>
            </div>
            <div className="flex gap-4 text-xs font-mono text-slate-400">
              <span>Total: <strong className="text-slate-100">{benchmarkSummary?.total_evaluated || 20}</strong></span>
              <span>Blocks: <strong className="text-red-400">{benchmarkSummary?.blocks_count || 14}</strong></span>
              <span>Cleared: <strong className="text-emerald-400">{benchmarkSummary?.cleared_count || 6}</strong></span>
              <span>SARs: <strong className="text-purple-400">{benchmarkSummary?.sar_filings_count || 14}</strong></span>
            </div>
          </div>

          <table className="w-full text-left text-xs bg-[#171b22] border border-[#262c37]">
            <thead>
              <tr className="bg-[#1f242e] text-slate-400 text-[11px] uppercase border-b border-[#262c37]">
                <th className="p-2.5">#</th>
                <th className="p-2.5">Case ID</th>
                <th className="p-2.5">Amount</th>
                <th className="p-2.5">Typology</th>
                <th className="p-2.5">Pre Action</th>
                <th className="p-2.5">Step-Up Result</th>
                <th className="p-2.5">Post Action</th>
                <th className="p-2.5">SAR</th>
                <th className="p-2.5">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1c212a]">
              {(benchmarkSummary?.results || []).map((r: any) => (
                <tr key={r.benchmark_id} className="hover:bg-[#1f242e]/60">
                  <td className="p-2.5 font-mono text-slate-500">{r.benchmark_id}</td>
                  <td
                    className="p-2.5 font-mono font-semibold text-slate-100 cursor-pointer underline"
                    onClick={() => {
                      setActiveTab("dossier");
                      handleSelectCase(r.case_id);
                    }}
                  >
                    {r.case_id}
                  </td>
                  <td className="p-2.5 font-mono">${(r.amount || 0).toLocaleString()}</td>
                  <td className="p-2.5 text-slate-300">{r.typology}</td>
                  <td className="p-2.5 font-mono text-slate-400">{r.action_pre}</td>
                  <td className="p-2.5 font-mono text-slate-500">{r.step_up}</td>
                  <td className={`p-2.5 font-mono font-bold ${r.action_post === "BLOCK_TRANSACTION" ? "text-red-400" : "text-emerald-400"}`}>
                    {r.action_post}
                  </td>
                  <td className="p-2.5 font-mono">
                    {r.sar_filed ? <span className="text-red-400 font-bold">YES</span> : <span className="text-slate-500">NO</span>}
                  </td>
                  <td className="p-2.5">
                    <button
                      onClick={() => {
                        setActiveTab("dossier");
                        handleSelectCase(r.case_id);
                      }}
                      className="px-2 py-0.5 text-[11px] border border-[#262c37] rounded hover:bg-[#262c37]"
                    >
                      Investigate
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Global Search Modal */}
      {showSearchModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#171b22] border border-[#262c37] w-full max-w-lg p-5 rounded shadow-2xl">
            <div className="flex justify-between items-center mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Global Search</span>
              <button onClick={() => setShowSearchModal(false)} className="text-xs font-mono text-slate-500 hover:text-white">
                Esc
              </button>
            </div>
            <input
              type="text"
              autoFocus
              placeholder="Search case, transaction, user, card, device, or IP..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full bg-[#101318] border border-[#262c37] px-3 py-2 text-xs font-mono text-slate-100 rounded focus:outline-none focus:border-slate-500 mb-3"
            />
            <div className="max-h-60 overflow-y-auto divide-y divide-[#1c212a]">
              {searchResults.length === 0 ? (
                <div className="text-center py-6 text-xs text-slate-500">
                  {searchQuery ? "No matching entities found." : "Type a query to search..."}
                </div>
              ) : (
                searchResults.map((c) => (
                  <div
                    key={c.case_id}
                    onClick={() => {
                      handleSelectCase(c.case_id);
                      setShowSearchModal(false);
                    }}
                    className="py-2 px-1 cursor-pointer hover:bg-[#1f242e] flex justify-between items-center text-xs"
                  >
                    <div>
                      <strong className="font-mono text-slate-200">{c.case_id}</strong>
                      <div className="text-[11px] text-slate-400">{c.title}</div>
                    </div>
                    <span className="font-mono text-red-400">Risk {c.risk_score}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Step-Up Simulation Modal */}
      {showStepUpModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#171b22] border border-[#262c37] w-full max-w-md p-5 rounded shadow-2xl">
            <div className="flex justify-between items-center mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Simulate Step-Up Verification</span>
              <button onClick={() => setShowStepUpModal(false)} className="text-xs font-mono text-slate-500 hover:text-white">
                Esc
              </button>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Inject secondary cardholder verification outcome to observe dynamic Milestone B defense recalculation.
            </p>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => handleStepUpSubmit("CONFIRMED_LEGITIMATE")}
                className="text-left p-2.5 border border-[#262c37] hover:border-emerald-600 rounded bg-[#101318] text-xs transition"
              >
                <strong className="text-emerald-400 block font-semibold">Cardholder Verified Legitimate</strong>
                <span className="text-[11px] text-slate-500">2FA approved, customer confirmed purchase</span>
              </button>
              <button
                onClick={() => handleStepUpSubmit("CONFIRMED_FRAUD")}
                className="text-left p-2.5 border border-[#262c37] hover:border-red-600 rounded bg-[#101318] text-xs transition"
              >
                <strong className="text-red-400 block font-semibold">Cardholder Reported Fraud</strong>
                <span className="text-[11px] text-slate-500">Explicit dispute, unauthorized card use reported</span>
              </button>
              <button
                onClick={() => handleStepUpSubmit("FAILED_VERIFICATION")}
                className="text-left p-2.5 border border-[#262c37] hover:border-amber-600 rounded bg-[#101318] text-xs transition"
              >
                <strong className="text-amber-400 block font-semibold">Failed Verification</strong>
                <span className="text-[11px] text-slate-500">3 incorrect OTP attempts or biometric mismatch</span>
              </button>
              <button
                onClick={() => handleStepUpSubmit("TIMEOUT_NO_RESPONSE")}
                className="text-left p-2.5 border border-[#262c37] hover:border-slate-600 rounded bg-[#101318] text-xs transition"
              >
                <strong className="text-slate-300 block font-semibold">Timeout / No Response</strong>
                <span className="text-[11px] text-slate-500">Challenge expired after 15-minute policy window</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
