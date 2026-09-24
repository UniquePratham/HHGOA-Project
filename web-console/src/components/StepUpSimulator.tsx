"use client";

import React, { useState } from "react";

interface StepUpSimulatorProps {
  currentStatus: string;
  onSimulate: (status: string, notes: string) => void;
  isLoading?: boolean;
}

export default function StepUpSimulator({
  currentStatus,
  onSimulate,
  isLoading = false,
}: StepUpSimulatorProps) {
  const [notes, setNotes] = useState("");
  const [pendingOption, setPendingOption] = useState<{
    status: string;
    label: string;
  } | null>(null);

  const options = [
    {
      status: "CONFIRMED_LEGITIMATE",
      label: "Cardholder Verified Legitimate",
      desc: "Simulate cardholder approving 2FA / biometric prompt.",
      style: "hover:border-emerald-600 border-slate-800 text-emerald-400",
      isDestructive: false,
    },
    {
      status: "CONFIRMED_FRAUD",
      label: "Cardholder Reported Fraud",
      desc: "Cardholder denies transaction. Immediate block triggered.",
      style: "hover:border-red-600 border-slate-800 text-red-400",
      isDestructive: true,
    },
    {
      status: "FAILED_VERIFICATION",
      label: "Step-Up Challenge Failed",
      desc: "3 incorrect OTP attempts or invalid biometric challenge.",
      style: "hover:border-amber-600 border-slate-800 text-amber-400",
      isDestructive: true,
    },
    {
      status: "TIMEOUT_NO_RESPONSE",
      label: "Challenge Expired (Timeout)",
      desc: "No response within policy window (15 mins). Risk escalates.",
      style: "hover:border-slate-600 border-slate-800 text-slate-300",
      isDestructive: false,
    },
  ];

  const handleSelect = (opt: (typeof options)[0]) => {
    if (opt.isDestructive) {
      setPendingOption(opt);
    } else {
      onSimulate(opt.status, notes || `Simulation: ${opt.label}`);
    }
  };

  const confirmPending = () => {
    if (pendingOption) {
      onSimulate(pendingOption.status, notes || `Simulation: ${pendingOption.label}`);
      setPendingOption(null);
    }
  };

  return (
    <div className="bg-slate-900/60 dark:bg-[#0f172a] border border-slate-800 rounded-xl p-5 flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between border-b border-slate-800 pb-3 gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
            <h3 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
              Step-Up Verification Sandbox
            </h3>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
              SIMULATED TESTING ENVIRONMENT
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-sans">
            Inject secondary cardholder verification outcomes to test graph state transitions.
          </p>
        </div>
        <div className="text-xs font-mono px-2.5 py-1 rounded bg-slate-950 border border-slate-800 text-slate-300">
          State: <span className="text-cyan-400 font-bold">{currentStatus}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {options.map((opt) => (
          <button
            key={opt.status}
            disabled={isLoading}
            onClick={() => handleSelect(opt)}
            className={`text-left p-3 rounded-lg border bg-slate-950/70 transition flex flex-col gap-1 ${
              opt.style
            } ${
              currentStatus === opt.status
                ? "ring-2 ring-cyan-500 bg-slate-900"
                : "hover:bg-slate-900"
            }`}
          >
            <span className="text-xs font-bold font-mono">{opt.label}</span>
            <span className="text-[11px] text-slate-400 leading-snug font-sans">{opt.desc}</span>
          </button>
        ))}
      </div>

      <div className="flex items-center gap-3 mt-1">
        <input
          type="text"
          placeholder="Optional analyst rationale or simulated customer call log..."
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
        />
      </div>

      {/* Confirmation Modal for Destructive Simulation */}
      {pendingOption && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 max-w-md w-full shadow-2xl">
            <h4 className="text-sm font-bold font-mono text-amber-400 uppercase mb-2">
              Confirm Step-Up Simulation Transition
            </h4>
            <p className="text-xs text-slate-300 mb-4 leading-relaxed font-sans">
              You are applying <strong className="text-white font-mono">{pendingOption.label}</strong>.
              This simulates customer dispute or verification failure, which initiates immediate transaction blocking and potential SAR filing.
            </p>
            <div className="flex justify-end gap-3 font-mono text-xs">
              <button
                onClick={() => setPendingOption(null)}
                className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={confirmPending}
                className="px-3 py-1.5 rounded bg-red-600 hover:bg-red-500 text-white font-bold"
              >
                Apply State Transition
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
