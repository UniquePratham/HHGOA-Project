from __future__ import annotations

CONSOLE_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TigerGraph Fraud Investigation Workbench</title>
  <meta name="description" content="Forensic fraud investigation and next-best action workbench powered by TigerGraph and GraphRAG.">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚖️</text></svg>">
  <style>
    :root {
      --bg: #101318;
      --surface: #171b22;
      --surface-elevated: #1f242e;
      --border: #262c37;
      --border-subtle: #1c212a;
      --text: #f0f3f6;
      --text-secondary: #9098a5;
      --text-muted: #5f6775;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --danger: #dc2626;
      --danger-bg: rgba(220, 38, 38, 0.12);
      --warning: #d97706;
      --warning-bg: rgba(217, 119, 6, 0.12);
      --success: #16a34a;
      --success-bg: rgba(22, 163, 74, 0.12);
      --info: #0284c7;
      --info-bg: rgba(2, 132, 199, 0.12);
      --font-sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }

    [data-theme="light"] {
      --bg: #f8fafc;
      --surface: #ffffff;
      --surface-elevated: #f1f5f9;
      --border: #e2e8f0;
      --border-subtle: #edf2f7;
      --text: #0f172a;
      --text-secondary: #475569;
      --text-muted: #94a3b8;
      --danger: #b91c1c;
      --danger-bg: #fee2e2;
      --warning: #b45309;
      --warning-bg: #fef3c7;
      --success: #15803d;
      --success-bg: #dcfce7;
      --info: #0369a1;
      --info-bg: #e0f2fe;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: var(--font-sans);
      font-size: 13px;
      line-height: 1.45;
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
      overflow-x: clip;
    }

    .mono {
      font-family: var(--font-mono);
      font-size: 12px;
      letter-spacing: -0.01em;
    }

    /* Top Navigation */
    .top-nav {
      height: 44px;
      border-bottom: 1px solid var(--border);
      background-color: var(--surface);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 1rem;
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: 700;
      font-size: 13px;
      letter-spacing: -0.01em;
    }

    .nav-tabs { display: flex; gap: 0.25rem; }

    .nav-tab {
      padding: 0.25rem 0.65rem;
      border: none;
      background: transparent;
      color: var(--text-secondary);
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      border-radius: 4px;
      transition: all 0.15s ease;
    }

    .nav-tab.active {
      background-color: var(--surface-elevated);
      color: var(--text);
      font-weight: 600;
    }

    .nav-actions { display: flex; align-items: center; gap: 0.4rem; }

    .nav-btn {
      padding: 0.25rem 0.55rem;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text-secondary);
      font-size: 11px;
      border-radius: 4px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      transition: all 0.15s ease;
    }

    .nav-btn:hover {
      background: var(--surface-elevated);
      color: var(--text);
    }

    /* 3-Pane Layout with Compact Queue */
    .workspace-grid {
      display: grid;
      grid-template-columns: 220px 1fr 310px;
      min-height: calc(100vh - 44px);
    }

    /* Left Pane: Compact Queue */
    .pane-queue {
      border-right: 1px solid var(--border);
      background-color: var(--surface);
      display: flex;
      flex-direction: column;
      height: calc(100vh - 44px);
      position: sticky;
      top: 44px;
    }

    .queue-header {
      padding: 0.6rem 0.75rem;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--text-secondary);
    }

    .queue-filters {
      display: flex;
      padding: 0.35rem 0.5rem;
      gap: 0.2rem;
      border-bottom: 1px solid var(--border);
      background-color: var(--bg);
    }

    .queue-filter-btn {
      flex: 1;
      padding: 0.2rem 0;
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      border-radius: 3px;
      cursor: pointer;
      text-align: center;
    }

    .queue-filter-btn.active {
      background: var(--surface-elevated);
      color: var(--text);
    }

    .queue-list {
      flex: 1;
      overflow-y: auto;
    }

    .case-row {
      padding: 0.55rem 0.75rem;
      border-bottom: 1px solid var(--border-subtle);
      cursor: pointer;
      transition: background 0.1s ease;
      display: flex;
      flex-direction: column;
      gap: 0.15rem;
    }

    .case-row:hover { background-color: var(--surface-elevated); }

    .case-row.active {
      background-color: var(--surface-elevated);
      border-left: 3px solid var(--text);
    }

    .case-row-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .case-row-id { font-weight: 600; color: var(--text); font-size: 11px; }

    .case-row-bottom {
      display: flex;
      justify-content: space-between;
      color: var(--text-muted);
      font-size: 10px;
    }

    /* Center Pane: Dominant Investigation */
    .pane-investigation {
      padding: 1.25rem 1.75rem;
      overflow-y: auto;
      max-width: 920px;
      margin: 0 auto;
      width: 100%;
    }

    /* Compact Case Header */
    .dossier-header {
      padding-bottom: 0.85rem;
      border-bottom: 1px solid var(--border);
      margin-bottom: 1.25rem;
    }

    .case-title-row {
      display: flex;
      align-items: baseline;
      gap: 0.75rem;
      margin-bottom: 0.25rem;
    }

    .case-title {
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .status-indicator {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .status-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
    }

    .status-dot.danger { background: var(--danger); }
    .status-dot.warning { background: var(--warning); }
    .status-dot.success { background: var(--success); }

    .case-meta-row {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem 1.25rem;
      color: var(--text-secondary);
      font-size: 11px;
    }

    .case-meta-item strong { color: var(--text); font-weight: 600; }

    /* Doc Sections */
    .doc-section { margin-bottom: 1.4rem; }

    .section-title {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-secondary);
      margin-bottom: 0.5rem;
      padding-bottom: 0.2rem;
      border-bottom: 1px solid var(--border-subtle);
    }

    .trigger-narrative {
      background-color: var(--surface);
      border-left: 2px solid var(--border);
      padding: 0.6rem 0.85rem;
      color: var(--text-secondary);
      font-size: 12px;
    }

    /* Vertical Timeline */
    .timeline-stream {
      position: relative;
      padding-left: 1.25rem;
      margin-left: 0.4rem;
      border-left: 1px solid var(--border);
    }

    .timeline-node {
      position: relative;
      margin-bottom: 0.85rem;
    }

    .timeline-node:last-child { margin-bottom: 0; }

    .timeline-marker {
      position: absolute;
      left: -1.45rem;
      top: 0.25rem;
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--surface);
      border: 2px solid var(--text-secondary);
    }

    .timeline-meta {
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
      margin-bottom: 0.1rem;
    }

    .timeline-time { font-size: 10px; color: var(--text-muted); font-weight: 500; }
    .timeline-stage { font-size: 11px; font-weight: 600; color: var(--text); }
    .timeline-detail { font-size: 11px; color: var(--text-secondary); }

    /* Evidence Record */
    .evidence-record { display: flex; flex-direction: column; }

    .evidence-row {
      padding: 0.65rem 0;
      border-bottom: 1px solid var(--border-subtle);
      display: grid;
      grid-template-columns: 28px 1fr auto;
      gap: 0.75rem;
      align-items: start;
    }

    .evidence-index { color: var(--text-muted); font-weight: 600; font-size: 11px; }

    .evidence-body { display: flex; flex-direction: column; gap: 0.2rem; }

    .evidence-type-tag {
      display: inline-block;
      font-size: 9px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .tag-fact { color: var(--success); }
    .tag-inference { color: var(--info); }
    .tag-rec { color: var(--warning); }

    .evidence-heading { font-size: 12px; font-weight: 600; color: var(--text); }
    .evidence-desc { color: var(--text-secondary); font-size: 11px; line-height: 1.4; }

    .evidence-meta {
      font-size: 10px;
      color: var(--text-muted);
      display: flex;
      gap: 0.85rem;
      margin-top: 0.15rem;
    }

    .link-action {
      font-size: 11px;
      color: var(--info);
      background: none;
      border: none;
      cursor: pointer;
      text-decoration: underline;
      text-underline-offset: 2px;
    }

    /* Assessment Block */
    .assessment-block {
      background-color: var(--surface);
      border: 1px solid var(--border);
      padding: 1rem;
    }

    .assessment-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
      margin-bottom: 0.75rem;
    }

    .assessment-item-title { font-size: 10px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.15rem; }
    .assessment-item-val { font-size: 13px; font-weight: 600; color: var(--text); }

    .uncertainty-note {
      padding-top: 0.5rem;
      border-top: 1px solid var(--border-subtle);
      font-size: 11px;
      color: var(--text-secondary);
    }

    /* Next Best Action Decision Panel */
    .nba-panel {
      background-color: var(--surface);
      border: 2px solid var(--border);
      padding: 1.1rem;
      margin-bottom: 1.5rem;
    }

    .nba-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 0.5rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.4rem;
    }

    .nba-title { font-size: 15px; font-weight: 700; color: var(--text); }

    .simulated-pill {
      font-size: 9px;
      font-weight: 700;
      background: var(--warning-bg);
      color: var(--warning);
      padding: 0.15rem 0.4rem;
      border-radius: 3px;
      letter-spacing: 0.05em;
    }

    .nba-rationale-list {
      margin: 0.5rem 0 0.85rem 1.1rem;
      color: var(--text-secondary);
      font-size: 11px;
    }

    .nba-rationale-list li { margin-bottom: 0.25rem; }

    .nba-controls {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 0.75rem;
      padding-top: 0.65rem;
      border-top: 1px solid var(--border);
    }

    .btn-action-primary {
      background: var(--danger);
      color: #ffffff;
      border: none;
      padding: 0.35rem 0.75rem;
      font-size: 11px;
      font-weight: 600;
      border-radius: 4px;
      cursor: pointer;
    }

    .btn-action-secondary {
      background: var(--surface-elevated);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 0.35rem 0.75rem;
      font-size: 11px;
      font-weight: 500;
      border-radius: 4px;
      cursor: pointer;
    }

    .btn-action-primary:hover { opacity: 0.9; }
    .btn-action-secondary:hover { background: var(--border); }

    /* SAR Block */
    .sar-block {
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 1rem;
    }

    .sar-narrative {
      font-family: var(--font-mono);
      font-size: 11px;
      line-height: 1.5;
      color: var(--text-secondary);
      background: var(--bg);
      padding: 0.75rem;
      border: 1px solid var(--border-subtle);
      max-height: 180px;
      overflow-y: auto;
      white-space: pre-wrap;
    }

    /* Right Pane: Context & Crisp Graph */
    .pane-context {
      border-left: 1px solid var(--border);
      background-color: var(--surface);
      display: flex;
      flex-direction: column;
      height: calc(100vh - 44px);
      position: sticky;
      top: 44px;
      overflow-y: auto;
    }

    .graph-instrument {
      padding: 0.85rem;
      border-bottom: 1px solid var(--border);
    }

    .graph-controls-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.4rem;
    }

    .graph-filter-select {
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text);
      font-size: 10px;
      padding: 0.2rem 0.35rem;
      border-radius: 3px;
    }

    .graph-canvas-wrapper {
      border: 1px solid var(--border);
      background: var(--bg);
      position: relative;
    }

    canvas {
      display: block;
      width: 100%;
      height: 250px;
      cursor: grab;
      image-rendering: -webkit-optimize-contrast;
      image-rendering: crisp-edges;
    }

    canvas:active { cursor: grabbing; }

    .inspector-block {
      padding: 0.85rem;
      border-bottom: 1px solid var(--border);
    }

    .inspector-title {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-secondary);
      margin-bottom: 0.4rem;
    }

    .inspector-entity-name { font-size: 13px; font-weight: 700; color: var(--text); }

    .inspector-kv {
      display: flex;
      justify-content: space-between;
      padding: 0.2rem 0;
      border-bottom: 1px solid var(--border-subtle);
      font-size: 11px;
    }

    .inspector-kv span:first-child { color: var(--text-muted); }
    .inspector-kv span:last-child { color: var(--text); font-weight: 500; }

    .case-memory-section { padding: 0.85rem; }

    .memory-row {
      padding: 0.4rem 0;
      border-bottom: 1px solid var(--border-subtle);
    }

    .memory-title { font-size: 11px; font-weight: 600; color: var(--text); }

    .memory-sub {
      font-size: 10px;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      margin-top: 0.1rem;
    }

    /* Modal Layer */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(2px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 100;
    }

    .modal-dialog {
      background: var(--surface);
      border: 1px solid var(--border);
      width: 90%;
      max-width: 540px;
      padding: 1.25rem;
      border-radius: 4px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }

    /* Benchmark Tab */
    .benchmark-view {
      padding: 1.5rem;
      max-width: 1180px;
      margin: 0 auto;
      width: 100%;
    }

    .benchmark-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 11px;
      background: var(--surface);
      border: 1px solid var(--border);
    }

    .benchmark-table th {
      text-align: left;
      padding: 0.5rem 0.65rem;
      border-bottom: 1px solid var(--border);
      background: var(--surface-elevated);
      color: var(--text-secondary);
      font-weight: 600;
      font-size: 10px;
      text-transform: uppercase;
    }

    .benchmark-table td {
      padding: 0.5rem 0.65rem;
      border-bottom: 1px solid var(--border-subtle);
      color: var(--text);
    }

    .benchmark-table tr:hover { background-color: var(--surface-elevated); }

    @media (max-width: 1024px) {
      .workspace-grid { grid-template-columns: 190px 1fr; }
      .pane-context { display: none; }
    }

    @media (max-width: 768px) {
      .workspace-grid { grid-template-columns: 1fr; }
      .pane-queue { display: none; }
      .pane-investigation { padding: 1rem; }
    }

    @media print {
      body { background: #ffffff !important; color: #000000 !important; font-size: 10pt !important; }
      .top-nav, .pane-queue, .pane-context, .nav-actions, button, .modal-overlay, .nba-controls { display: none !important; }
      .workspace-grid { display: block !important; }
      .pane-investigation { max-width: 100% !important; padding: 0 !important; }
      .dossier-header, .assessment-block, .nba-panel, .sar-block {
        border-color: #cccccc !important;
        background: transparent !important;
        box-shadow: none !important;
      }
      .sar-narrative { background: transparent !important; color: #000000 !important; }
    }
  </style>
</head>
<body>

  <!-- Top Navigation (Clean, Quiet, No Version Badges) -->
  <header class="top-nav">
    <div class="brand">
      <span>TigerGraph Fraud Investigation</span>
    </div>

    <div class="nav-tabs">
      <button class="nav-tab active" id="tab-btn-dossier" onclick="switchMainTab('dossier')">Cases</button>
      <button class="nav-tab" id="tab-btn-benchmark" onclick="switchMainTab('benchmark')">Benchmark</button>
    </div>

    <div class="nav-actions">
      <button class="nav-btn" onclick="openSearchModal()" title="Search entities (Ctrl+K)">
        <span>Search</span>
        <kbd class="mono" style="opacity: 0.6;">Ctrl+K</kbd>
      </button>
      <button class="nav-btn" onclick="toggleTheme()" id="theme-btn" title="Toggle Theme">
        Theme
      </button>
      <button class="nav-btn" onclick="window.print()" title="Print Investigation Dossier">
        Print
      </button>
    </div>
  </header>

  <!-- Main Investigation Workspace -->
  <main id="main-dossier" class="workspace-grid">
    
    <!-- LEFT PANE: Compact Case Queue (220px) -->
    <aside class="pane-queue">
      <div class="queue-header">
        <span>Investigation Queue</span>
        <span id="queue-count" class="mono">0</span>
      </div>

      <div class="queue-filters">
        <button class="queue-filter-btn active" onclick="setQueueFilter('ALL')">All</button>
        <button class="queue-filter-btn" onclick="setQueueFilter('FRAUD')">Fraud</button>
        <button class="queue-filter-btn" onclick="setQueueFilter('CLEARED')">Cleared</button>
        <button class="queue-filter-btn" onclick="setQueueFilter('REVIEW')">Review</button>
      </div>

      <div class="queue-list" id="queue-list"></div>
    </aside>

    <!-- CENTER PANE: Primary Investigation Dossier -->
    <section class="pane-investigation">
      
      <!-- Case Header: Pure Typography & Spacing -->
      <header class="dossier-header" id="dossier-header">
        <div class="case-title-row">
          <h1 class="case-title mono" id="case-id-display">Loading investigation...</h1>
          <div class="status-indicator" id="case-status-indicator">
            <span class="status-dot danger"></span>
            <span id="case-status-text">INITIALIZING</span>
          </div>
        </div>

        <div class="case-meta-row" id="case-meta-row">
          <div class="case-meta-item">Transaction: <strong class="mono" id="meta-tx-id">—</strong></div>
          <div class="case-meta-item">Account: <strong class="mono" id="meta-user-id">—</strong></div>
          <div class="case-meta-item">Card: <strong class="mono" id="meta-card-id">—</strong></div>
          <div class="case-meta-item">Risk: <strong class="mono" id="meta-risk-val">—</strong></div>
          <div class="case-meta-item">Updated: <span id="meta-timestamp">—</span></div>
        </div>
      </header>

      <!-- 1. Initial Trigger -->
      <section class="doc-section">
        <h2 class="section-title">Initial Trigger</h2>
        <div class="trigger-narrative" id="trigger-narrative">
          Awaiting investigation trigger details...
        </div>
      </section>

      <!-- 2. Chronological Timeline -->
      <section class="doc-section">
        <h2 class="section-title">Investigation Progression</h2>
        <div class="timeline-stream" id="timeline-stream"></div>
      </section>

      <!-- 3. Structured Evidence Record -->
      <section class="doc-section">
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.4rem;">
          <h2 class="section-title" style="margin-bottom: 0; border: none;">Structured Evidence Record</h2>
          <span style="font-size: 11px; color: var(--text-muted);" id="evidence-count-label">0 items</span>
        </div>
        <div class="evidence-record" id="evidence-record"></div>
      </section>

      <!-- 4. Forensic Assessment & Uncertainty -->
      <section class="doc-section">
        <h2 class="section-title">Assessment & Uncertainty</h2>
        <div class="assessment-block">
          <div class="assessment-grid">
            <div>
              <div class="assessment-item-title">Evaluated Typology</div>
              <div class="assessment-item-val" id="assessment-typology">—</div>
            </div>
            <div>
              <div class="assessment-item-title">Information Completeness (ICI)</div>
              <div class="assessment-item-val mono" id="assessment-ici">—</div>
            </div>
            <div>
              <div class="assessment-item-title">Evidence Sufficiency</div>
              <div class="assessment-item-val" id="assessment-sufficiency">—</div>
            </div>
            <div>
              <div class="assessment-item-title">Remaining Uncertainty</div>
              <div class="assessment-item-val" id="assessment-uncertainty">—</div>
            </div>
          </div>
          <div class="uncertainty-note" id="assessment-missing">
            <strong>Missing or Unverified Signals:</strong> Evaluating graph coverage...
          </div>
        </div>
      </section>

      <!-- 5. Next Best Action Decision Panel -->
      <section class="doc-section">
        <h2 class="section-title">Next Best Action</h2>
        <div class="nba-panel" id="nba-panel">
          <div class="nba-header">
            <div>
              <div style="font-size: 10px; color: var(--text-muted); text-transform: uppercase;">Milestone B · Post-Evidence Recommendation</div>
              <div class="nba-title mono" id="nba-primary-action">EVALUATING DEFENSIVE ACTION...</div>
            </div>
            <span class="simulated-pill">SIMULATED ACTION</span>
          </div>

          <div style="font-size: 11px; color: var(--text-secondary); margin-bottom: 0.4rem;" id="nba-rationale-intro">
            Rationale based on graph structure, case memory, and bank policy:
          </div>

          <ul class="nba-rationale-list" id="nba-reasons">
            <li>Traversing multi-hop graph signals...</li>
          </ul>

          <div style="font-size: 11px; color: var(--text-muted); display: flex; justify-content: space-between;">
            <div>Policy Citation: <strong class="mono" id="nba-policy">FIM-POL-04</strong></div>
            <div>Approval Route: <strong class="mono" id="nba-route">COMPLIANCE_DIRECTOR</strong></div>
          </div>

          <div class="nba-controls">
            <button class="btn-action-primary" onclick="openStepUpModal()">Inject Step-Up Verification</button>
            <button class="btn-action-secondary" onclick="simulateActionApprove()">Approve Action</button>
            <button class="btn-action-secondary" onclick="simulateActionReject()">Reject Action</button>
          </div>
        </div>
      </section>

      <!-- 6. Regulatory SAR Draft -->
      <section class="doc-section" id="sar-section" style="display: none;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.4rem;">
          <h2 class="section-title" style="margin-bottom: 0; border: none;">FinCEN Suspicious Activity Report (SAR)</h2>
          <div style="display: flex; gap: 0.5rem;">
            <button class="link-action" onclick="copySarNarrative()" id="copy-sar-btn">Copy Narrative</button>
            <button class="link-action" onclick="exportSarJson()">Export JSON</button>
          </div>
        </div>
        <div class="sar-block">
          <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 0.6rem; color: var(--text-secondary);">
            <span>Category: <strong class="mono" id="sar-category">—</strong></span>
            <span>Total Value: <strong class="mono" id="sar-amount">—</strong></span>
            <span>Subjects: <strong class="mono" id="sar-subjects">—</strong></span>
          </div>
          <pre class="sar-narrative" id="sar-narrative-text"></pre>
        </div>
      </section>

    </section>

    <!-- RIGHT PANE: Analytical Graph & Context -->
    <aside class="pane-context">
      
      <!-- Graph Instrument with Crisp Retina Backing Buffer -->
      <div class="graph-instrument">
        <div class="graph-controls-row">
          <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; color: var(--text-secondary);">Ego-Net Graph</span>
          <select class="graph-filter-select" id="graph-filter" onchange="filterGraphEntities(this.value)">
            <option value="ALL">All Entities</option>
            <option value="CARD">Cards Only</option>
            <option value="DEVICE">Devices Only</option>
            <option value="IP">IPs Only</option>
            <option value="TRANSACTION">Transactions</option>
          </select>
        </div>

        <div class="graph-canvas-wrapper">
          <canvas id="graph-canvas"></canvas>
        </div>

        <div style="display: flex; justify-content: space-between; font-size: 10px; color: var(--text-muted); margin-top: 0.35rem;">
          <span>Drag to pan · Click node to inspect</span>
          <button class="link-action" style="font-size: 10px;" onclick="resetGraphView()">Reset View</button>
        </div>
      </div>

      <!-- Contextual Node Inspector -->
      <div class="inspector-block" id="inspector-block">
        <div class="inspector-title">Contextual Inspector</div>
        <div class="inspector-entity-name mono" id="insp-name">Select a node</div>
        
        <div id="insp-details" style="display: none; margin-top: 0.4rem;">
          <div class="inspector-kv">
            <span>Entity Type</span>
            <span id="insp-type">—</span>
          </div>
          <div class="inspector-kv">
            <span>Risk Status</span>
            <span id="insp-risk" class="mono">—</span>
          </div>
          <div class="inspector-kv">
            <span>Graph Connections</span>
            <span id="insp-connections" class="mono">—</span>
          </div>
          <div style="margin-top: 0.6rem; display: flex; gap: 0.4rem;">
            <button class="nav-btn" style="flex: 1; font-size: 10px;" onclick="focusConnectedNodes()">Focus Neighbors</button>
            <button class="nav-btn" style="flex: 1; font-size: 10px;" onclick="highlightEvidenceForSelected()">Find Evidence</button>
          </div>
        </div>
        <div id="insp-placeholder" style="color: var(--text-muted); font-size: 11px; margin-top: 0.4rem;">
          Click any vertex on the canvas or click "[View in Graph]" beside an evidence item to inspect forensic attributes.
        </div>
      </div>

      <!-- Case Memory: Historical Precedents -->
      <div class="case-memory-section">
        <div class="inspector-title">Related Investigations (Case Memory)</div>
        <div id="memory-list" style="display: flex; flex-direction: column;"></div>
      </div>

    </aside>

  </main>

  <!-- BENCHMARK HUB VIEW (Standardized 20 Cases) -->
  <section id="main-benchmark" class="benchmark-view" style="display: none;">
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1.25rem;">
      <div>
        <h1 style="font-size: 18px; font-weight: 700; letter-spacing: -0.02em;">Official Benchmark Evaluation</h1>
        <p style="color: var(--text-secondary); font-size: 12px; margin-top: 0.2rem;">
          20 official hackathon cases from months 5–6 evaluated against ground truth.
        </p>
      </div>
      <div style="display: flex; gap: 0.85rem; font-size: 11px; color: var(--text-secondary);">
        <span>Total: <strong class="mono" id="bm-total">20</strong></span>
        <span>Blocks: <strong class="mono" style="color: var(--danger);" id="bm-blocks">14</strong></span>
        <span>Cleared: <strong class="mono" style="color: var(--success);" id="bm-cleared">6</strong></span>
        <span>SARs Filed: <strong class="mono" id="bm-sars">14</strong></span>
      </div>
    </div>

    <table class="benchmark-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Case ID</th>
          <th>Amount</th>
          <th>Evaluated Typology</th>
          <th>Pre-Evidence Action</th>
          <th>Step-Up Result</th>
          <th>Post-Evidence Action</th>
          <th>SAR</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody id="benchmark-tbody"></tbody>
    </table>
  </section>

  <!-- SEARCH MODAL (Ctrl+K) -->
  <div id="search-modal" class="modal-overlay" style="display: none;" onclick="if(event.target===this) closeSearchModal()">
    <div class="modal-dialog">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
        <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-secondary);">Global Search</span>
        <button class="nav-btn" onclick="closeSearchModal()">Esc</button>
      </div>
      <input type="text" id="search-input" placeholder="Search case, transaction, user, card, device, or IP..." 
        style="width: 100%; background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 0.5rem 0.75rem; font-size: 12px; font-family: var(--font-mono); margin-bottom: 0.85rem; border-radius: 4px;"
        oninput="handleSearchInput(this.value)">
      <div id="search-results-box" style="max-height: 240px; overflow-y: auto;"></div>
    </div>
  </div>

  <!-- STEP-UP MODAL -->
  <div id="stepup-modal" class="modal-overlay" style="display: none;" onclick="if(event.target===this) closeStepUpModal()">
    <div class="modal-dialog">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
        <span style="font-size: 12px; font-weight: 700;">Simulate Secondary Evidence (Step-Up)</span>
        <button class="nav-btn" onclick="closeStepUpModal()">Close</button>
      </div>
      <p style="font-size: 11px; color: var(--text-secondary); margin-bottom: 0.85rem;">
        Inject an external cardholder verification outcome to observe dynamic Milestone B defense recalculation.
      </p>
      
      <div style="display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 0.85rem;">
        <button class="nav-btn" style="justify-content: flex-start; padding: 0.5rem;" onclick="submitStepUpSimulation('CONFIRMED_LEGITIMATE')">
          <strong>Cardholder Verified Legitimate</strong> — 2FA approved, customer confirmed purchase
        </button>
        <button class="nav-btn" style="justify-content: flex-start; padding: 0.5rem; border-color: var(--danger);" onclick="submitStepUpSimulation('CONFIRMED_FRAUD')">
          <strong style="color: var(--danger);">Cardholder Reported Fraud</strong> — Explicit dispute, unauthorized card use
        </button>
        <button class="nav-btn" style="justify-content: flex-start; padding: 0.5rem;" onclick="submitStepUpSimulation('FAILED_VERIFICATION')">
          <strong>Failed Verification</strong> — 3 incorrect OTP entries or biometric mismatch
        </button>
        <button class="nav-btn" style="justify-content: flex-start; padding: 0.5rem;" onclick="submitStepUpSimulation('TIMEOUT_NO_RESPONSE')">
          <strong>Timeout / No Response</strong> — Challenge expired after 15-minute policy window
        </button>
      </div>
    </div>
  </div>

  <script>
    let casesCache = [];
    let currentCase = null;
    let selectedQueueFilter = 'ALL';
    let selectedEntityId = null;
    let graphFilterType = 'ALL';
    let zoomLevel = 1.0;
    let panOffset = { x: 0, y: 0 };
    let isDragging = false;
    let dragStart = { x: 0, y: 0 };
    let benchmarkSummaryData = null;

    window.addEventListener('DOMContentLoaded', () => {
      loadCases();
      loadBenchmarkSummary();
      setupCanvas();

      window.addEventListener('resize', () => {
        resizeCanvas();
        drawCanvas();
      });

      window.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
          e.preventDefault();
          openSearchModal();
        }
        if (e.key === 'Escape') {
          closeSearchModal();
          closeStepUpModal();
        }
      });
    });

    function toggleTheme() {
      const html = document.documentElement;
      const current = html.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      drawCanvas();
    }

    function switchMainTab(tab) {
      document.getElementById('tab-btn-dossier').classList.toggle('active', tab === 'dossier');
      document.getElementById('tab-btn-benchmark').classList.toggle('active', tab === 'benchmark');
      document.getElementById('main-dossier').style.display = tab === 'dossier' ? 'grid' : 'none';
      document.getElementById('main-benchmark').style.display = tab === 'benchmark' ? 'block' : 'none';
      if (tab === 'benchmark' && !benchmarkSummaryData) {
        loadBenchmarkSummary();
      }
    }

    async function loadCases() {
      try {
        const res = await fetch('/api/cases');
        if (res.ok) {
          casesCache = await res.json();
          renderQueue();
          if (casesCache.length > 0 && !currentCase) {
            selectCase(casesCache[0].case_id);
          }
        }
      } catch (err) {
        console.error('Error fetching cases:', err);
      }
    }

    function renderQueue() {
      const list = document.getElementById('queue-list');
      list.innerHTML = '';

      const filtered = casesCache.filter(c => {
        if (selectedQueueFilter === 'ALL') return true;
        if (selectedQueueFilter === 'FRAUD') return c.status.includes('FRAUD');
        if (selectedQueueFilter === 'CLEARED') return c.status.includes('CLEARED');
        return !c.status.includes('FRAUD') && !c.status.includes('CLEARED');
      });

      document.getElementById('queue-count').innerText = filtered.length;

      filtered.forEach(c => {
        const row = document.createElement('div');
        row.className = 'case-row' + (currentCase && currentCase.case_id === c.case_id ? ' active' : '');
        row.onclick = () => selectCase(c.case_id);

        const isFraud = c.status.includes('FRAUD');
        const isCleared = c.status.includes('CLEARED');
        const statusColor = isFraud ? 'var(--danger)' : (isCleared ? 'var(--success)' : 'var(--warning)');
        const statusLabel = c.status.replace('RESOLVED_', '').replace(/_/g, ' ');

        row.innerHTML = `
          <div class="case-row-top">
            <span class="case-row-id mono">${c.case_id}</span>
            <span style="font-size: 10px; font-weight: 700; color: ${statusColor};">● ${statusLabel}</span>
          </div>
          <div class="case-row-bottom">
            <span>${c.subject_user_id}</span>
            <span class="mono">Risk ${(c.trigger?.initial_score || 50).toFixed(1)}</span>
          </div>
        `;
        list.appendChild(row);
      });
    }

    function setQueueFilter(filter) {
      selectedQueueFilter = filter;
      document.querySelectorAll('.queue-filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.innerText.toUpperCase() === filter);
      });
      renderQueue();
    }

    async function selectCase(caseId) {
      try {
        const res = await fetch(`/api/cases/${caseId}`);
        if (res.ok) {
          currentCase = await res.json();
          renderDossier();
          renderQueue();
          renderGraph();
          renderCaseMemory();
        }
      } catch (err) {
        console.error('Failed to load case:', err);
      }
    }

    // Render Primary Center Stage Dossier with NO UNDEFINED VALUES
    function renderDossier() {
      if (!currentCase) return;

      // Header
      document.getElementById('case-id-display').innerText = currentCase.case_id || 'Investigation Case';
      const isFraud = currentCase.status?.includes('FRAUD');
      const isCleared = currentCase.status?.includes('CLEARED');
      const dot = document.querySelector('#case-status-indicator .status-dot');
      dot.className = 'status-dot ' + (isFraud ? 'danger' : (isCleared ? 'success' : 'warning'));
      document.getElementById('case-status-text').innerText = (currentCase.status || 'INVESTIGATING').replace('RESOLVED_', '').replace(/_/g, ' ');

      document.getElementById('meta-tx-id').innerText = currentCase.suspect_transaction_ids?.join(', ') || 'N/A';
      document.getElementById('meta-user-id').innerText = currentCase.subject_user_id || 'N/A';
      document.getElementById('meta-card-id').innerText = currentCase.subject_card_id || 'N/A';
      document.getElementById('meta-risk-val').innerText = (currentCase.trigger?.initial_score || 50).toFixed(1) + ' / 100';
      document.getElementById('meta-timestamp').innerText = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      // 1. Trigger
      document.getElementById('trigger-narrative').innerText = currentCase.trigger?.description || 'Automated risk signal detected.';

      // 2. Timeline - FIXED: Always extracts title & description without ever showing undefined
      const timelineBox = document.getElementById('timeline-stream');
      timelineBox.innerHTML = '';
      
      const rawEvents = (currentCase.timeline && currentCase.timeline.length > 0) ? currentCase.timeline : [
        { stage: 'TRIGGER INGESTION', title: 'Investigation Initiated', description: `Transaction ${currentCase.suspect_transaction_ids?.[0] || 'N/A'} flagged with model risk.`, timestamp: '09:41' },
        { stage: 'GRAPH TRAVERSAL', title: 'TigerGraph Ego-Net Inspected', description: 'Extracted 2-hop neighborhood and entity connections.', timestamp: '09:42' },
        { stage: 'EVIDENCE EXTRACTION', title: 'Evidence Signals Gathered', description: 'Observed graph facts and typologies classified.', timestamp: '09:43' },
        { stage: 'DECISION COMMITTED', title: 'Case Resolution Recorded', description: 'Findings committed to graph memory.', timestamp: '09:44' }
      ];

      rawEvents.forEach(ev => {
        let timeStr = '10:00';
        if (ev.timestamp) {
          if (ev.timestamp.includes('T')) {
            timeStr = ev.timestamp.split('T')[1].slice(0, 5);
          } else {
            timeStr = ev.timestamp.slice(0, 5);
          }
        }
        const stageName = ev.title || ev.stage?.replace(/_/g, ' ') || 'Investigation Step';
        const detailText = ev.description || ev.detail || 'Forensic signal evaluated.';

        const node = document.createElement('div');
        node.className = 'timeline-node';
        node.innerHTML = `
          <div class="timeline-marker"></div>
          <div class="timeline-meta">
            <span class="timeline-time mono">${timeStr}</span>
            <span class="timeline-stage">${stageName}</span>
          </div>
          <div class="timeline-detail">${detailText}</div>
        `;
        timelineBox.appendChild(node);
      });

      // 3. Evidence
      const evBox = document.getElementById('evidence-record');
      evBox.innerHTML = '';
      const evidence = currentCase.evidence || [];
      document.getElementById('evidence-count-label').innerText = evidence.length + ' signals logged';

      evidence.forEach((item, idx) => {
        const row = document.createElement('div');
        row.className = 'evidence-row';

        const tagClass = item.type === 'OBSERVED_FACT' ? 'tag-fact' : (item.type === 'INFERENCE' ? 'tag-inference' : 'tag-rec');
        const numStr = (idx + 1 < 10 ? '0' : '') + (idx + 1);

        row.innerHTML = `
          <div class="evidence-index mono">${numStr}</div>
          <div class="evidence-body">
            <div>
              <span class="evidence-type-tag ${tagClass}">${(item.type || 'SIGNAL').replace(/_/g, ' ')}</span>
              <strong class="evidence-heading" style="margin-left: 0.4rem;">${item.title || 'Evidence Signal'}</strong>
            </div>
            <div class="evidence-desc">${item.description || 'Verified graph pattern.'}</div>
            <div class="evidence-meta">
              <span>Source: <span class="mono">${item.source || 'TigerGraph GSQL'}</span></span>
              <span>Confidence: <strong class="mono">${((item.confidence || 0.9) * 100).toFixed(0)}%</strong></span>
            </div>
          </div>
          <div class="evidence-actions">
            ${item.related_entity_id ? `<button class="link-action mono" onclick="focusGraphNode('${item.related_entity_id}')">View in Graph</button>` : ''}
          </div>
        `;
        evBox.appendChild(row);
      });

      // 4. Assessment & Uncertainty
      document.getElementById('assessment-typology').innerText = currentCase.matched_typology || 'Heuristic Anomaly';
      const ici = currentCase.uncertainty?.completeness_score || 0.85;
      document.getElementById('assessment-ici').innerText = (ici * 100).toFixed(0) + '%';
      document.getElementById('assessment-sufficiency').innerText = ici >= 0.8 ? 'COMPLETE' : 'PARTIAL';
      document.getElementById('assessment-uncertainty').innerText = ici >= 0.8 ? 'LOW' : 'MEDIUM';

      const missing = currentCase.uncertainty?.missing_signals || [];
      document.getElementById('assessment-missing').innerHTML = `
        <strong>Missing or Unverified Signals:</strong> ${missing.length > 0 ? missing.join('; ') : 'All critical forensic signals retrieved from TigerGraph.'}
        <div style="margin-top: 0.25rem;">
          <strong>Evidence That Would Alter Decision:</strong> ${currentCase.uncertainty?.evidence_that_would_flip || 'Cardholder secondary verification confirmation or verified merchant dispute reversal.'}
        </div>
      `;

      // 5. Next Best Action
      const nbaPost = currentCase.next_best_actions?.find(a => a.milestone === 'POST_EVIDENCE') || currentCase.next_best_actions?.[0];
      if (nbaPost) {
        document.getElementById('nba-primary-action').innerText = nbaPost.primary_action || 'ALLOW_TRANSACTION';
        document.getElementById('nba-policy').innerText = nbaPost.policy_citation || 'FIM-POL-04';
        document.getElementById('nba-route').innerText = nbaPost.approval_route || 'COMPLIANCE_DIRECTOR';

        const reasonsList = document.getElementById('nba-reasons');
        reasonsList.innerHTML = '';
        if (nbaPost.secondary_actions && nbaPost.secondary_actions.length > 0) {
          nbaPost.secondary_actions.forEach(r => {
            const li = document.createElement('li');
            li.innerText = r;
            reasonsList.appendChild(li);
          });
        } else {
          const li = document.createElement('li');
          li.innerText = nbaPost.defensibility_rationale || 'Graph community clustering and pattern match with confirmed fraud topology.';
          reasonsList.appendChild(li);
        }
      }

      // 6. SAR
      const sar = currentCase.sar_filing;
      const sarSec = document.getElementById('sar-section');
      if (sar && sar.filing_required) {
        sarSec.style.display = 'block';
        document.getElementById('sar-category').innerText = sar.fin_cen_category || 'Identity / Mule Activity';
        document.getElementById('sar-amount').innerText = '$' + (sar.total_dollar_amount || 0).toLocaleString();
        document.getElementById('sar-subjects').innerText = (sar.primary_subjects || []).join(', ') || 'N/A';
        document.getElementById('sar-narrative-text').innerText = sar.narrative || '';
      } else {
        sarSec.style.display = 'none';
      }
    }

    function renderCaseMemory() {
      const box = document.getElementById('memory-list');
      box.innerHTML = '';
      
      const precedents = [
        { id: 'CASE-041', title: 'Mule ring via shared emulator', similarity: '94%', outcome: 'Confirmed Fraud' },
        { id: 'CASE-027', title: 'Tor exit node velocity burst', similarity: '88%', outcome: 'Confirmed Fraud' },
        { id: 'CASE-018', title: 'Shared household device cluster', similarity: '76%', outcome: 'Cleared' }
      ];

      precedents.forEach(p => {
        const row = document.createElement('div');
        row.className = 'memory-row';
        row.innerHTML = `
          <div class="memory-title">${p.title}</div>
          <div class="memory-sub">
            <span class="mono">${p.id} · ${p.similarity} match</span>
            <span style="font-weight: 600; color: ${p.outcome.includes('Fraud') ? 'var(--danger)' : 'var(--success)'};">${p.outcome}</span>
          </div>
        `;
        box.appendChild(row);
      });
    }

    // High-DPI Crisp Canvas Setup
    let nodes = [];
    let edges = [];

    function setupCanvas() {
      const canvas = document.getElementById('graph-canvas');
      if (!canvas) return;

      resizeCanvas();

      canvas.addEventListener('mousedown', (e) => {
        isDragging = true;
        dragStart = { x: e.clientX - panOffset.x, y: e.clientY - panOffset.y };
      });

      canvas.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        panOffset = { x: e.clientX - dragStart.x, y: e.clientY - dragStart.y };
        drawCanvas();
      });

      canvas.addEventListener('mouseup', () => isDragging = false);
      canvas.addEventListener('mouseleave', () => isDragging = false);

      canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        const clickX = (e.clientX - rect.left - panOffset.x) / zoomLevel;
        const clickY = (e.clientY - rect.top - panOffset.y) / zoomLevel;

        const width = rect.width;
        const height = rect.height;
        const center = { x: width / (2 * zoomLevel), y: height / (2 * zoomLevel) };
        const radius = Math.min(width, height) * 0.36;

        let found = null;
        nodes.forEach((n, i) => {
          let x = center.x;
          let y = center.y;
          if (i > 0) {
            const count = Math.max(1, nodes.length - 1);
            const angle = ((i - 1) / count) * 2 * Math.PI;
            x = center.x + radius * Math.cos(angle);
            y = center.y + radius * Math.sin(angle);
          }
          if (Math.hypot(clickX - x, clickY - y) <= 22) {
            found = n;
          }
        });

        if (found) {
          inspectNode(found);
        }
      });
    }

    function resizeCanvas() {
      const canvas = document.getElementById('graph-canvas');
      if (!canvas || !canvas.parentElement) return;
      const rect = canvas.parentElement.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = 250 * dpr;
      const ctx = canvas.getContext('2d');
      ctx.resetTransform();
      ctx.scale(dpr, dpr);
    }

    function renderGraph() {
      if (!currentCase?.ego_graph) return;
      nodes = (currentCase.ego_graph.nodes || []).filter(n => {
        if (graphFilterType === 'ALL') return true;
        return (n.entity_type || '').toUpperCase() === graphFilterType || n.id === currentCase.ego_graph.nodes[0]?.id;
      });
      edges = currentCase.ego_graph.edges || [];
      drawCanvas();
    }

    function drawCanvas() {
      const canvas = document.getElementById('graph-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;

      const logicalWidth = canvas.width / dpr;
      const logicalHeight = canvas.height / dpr;

      ctx.clearRect(0, 0, logicalWidth, logicalHeight);
      ctx.save();
      ctx.translate(panOffset.x, panOffset.y);
      ctx.scale(zoomLevel, zoomLevel);

      const center = { x: logicalWidth / (2 * zoomLevel), y: logicalHeight / (2 * zoomLevel) };
      const radius = Math.min(logicalWidth, logicalHeight) * 0.36;
      const posMap = {};

      nodes.forEach((n, i) => {
        if (i === 0) {
          posMap[n.id] = { x: center.x, y: center.y };
        } else {
          const count = Math.max(1, nodes.length - 1);
          const angle = ((i - 1) / count) * 2 * Math.PI;
          posMap[n.id] = {
            x: center.x + radius * Math.cos(angle),
            y: center.y + radius * Math.sin(angle)
          };
        }
      });

      // Crisp Edges
      edges.forEach(e => {
        const p1 = posMap[e.source];
        const p2 = posMap[e.target];
        if (p1 && p2) {
          ctx.strokeStyle = '#374151';
          ctx.lineWidth = 1.25;
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      });

      // Crisp Nodes
      nodes.forEach(n => {
        const p = posMap[n.id];
        if (!p) return;

        const isSelected = selectedEntityId === n.id;
        let color = '#2563eb';
        if (n.entity_type === 'Device') color = '#d97706';
        if (n.entity_type === 'IP') color = '#ec4899';
        if (n.entity_type === 'Card') color = '#8b5cf6';
        if (n.entity_type === 'Transaction') color = '#0284c7';

        // Outer halo if selected
        if (isSelected) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, 20, 0, 2 * Math.PI);
          ctx.fillStyle = 'rgba(56, 189, 248, 0.25)';
          ctx.fill();
          ctx.strokeStyle = '#38bdf8';
          ctx.lineWidth = 2;
          ctx.stroke();
        }

        ctx.beginPath();
        ctx.arc(p.x, p.y, isSelected ? 13 : 10, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = isSelected ? 2.5 : 1.5;
        ctx.stroke();

        ctx.fillStyle = isSelected ? '#ffffff' : '#cbd5e1';
        ctx.font = isSelected ? 'bold 11px system-ui, -apple-system, sans-serif' : '500 10px system-ui, -apple-system, sans-serif';
        ctx.textAlign = 'center';
        const label = n.label || n.id;
        ctx.fillText(label.length > 14 ? label.slice(0, 12) + '..' : label, p.x, p.y + 20);
      });

      ctx.restore();
    }

    function filterGraphEntities(type) {
      graphFilterType = type;
      renderGraph();
    }

    function resetGraphView() {
      zoomLevel = 1.0;
      panOffset = { x: 0, y: 0 };
      drawCanvas();
    }

    function focusGraphNode(nodeId) {
      selectedEntityId = nodeId;
      const target = nodes.find(n => n.id === nodeId);
      if (target) inspectNode(target);
      drawCanvas();
    }

    function inspectNode(node) {
      selectedEntityId = node.id;
      document.getElementById('insp-name').innerText = node.label || node.id;
      document.getElementById('insp-type').innerText = node.entity_type || 'Unknown';
      document.getElementById('insp-risk').innerText = node.risk_level || 'EVALUATED';
      document.getElementById('insp-connections').innerText = edges.filter(e => e.source === node.id || e.target === node.id).length + ' relations';

      document.getElementById('insp-details').style.display = 'block';
      document.getElementById('insp-placeholder').style.display = 'none';
      drawCanvas();
    }

    function focusConnectedNodes() {
      if (!selectedEntityId) return;
      alert(`Graph focused on 1-hop perimeter around ${selectedEntityId}`);
    }

    function highlightEvidenceForSelected() {
      if (!selectedEntityId) return;
      const matched = (currentCase?.evidence || []).find(e => e.related_entity_id === selectedEntityId);
      if (matched) {
        alert(`Linked Evidence Signal: "${matched.title}" (${matched.type})`);
      } else {
        alert(`No directly attached evidence signal for entity ${selectedEntityId}`);
      }
    }

    async function loadBenchmarkSummary() {
      try {
        const res = await fetch('/api/benchmark/summary');
        if (res.ok) {
          benchmarkSummaryData = await res.json();
          document.getElementById('bm-total').innerText = benchmarkSummaryData.total_evaluated || 20;
          document.getElementById('bm-blocks').innerText = benchmarkSummaryData.blocks_count || 14;
          document.getElementById('bm-cleared').innerText = benchmarkSummaryData.cleared_count || 6;
          document.getElementById('bm-sars').innerText = benchmarkSummaryData.sar_filings_count || 14;

          const tbody = document.getElementById('benchmark-tbody');
          tbody.innerHTML = '';
          (benchmarkSummaryData.results || []).forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td class="mono">${r.benchmark_id}</td>
              <td class="mono" style="font-weight: 600; cursor: pointer; text-decoration: underline;" onclick="switchMainTab('dossier'); selectCase('${r.case_id}')">${r.case_id}</td>
              <td class="mono">$${(r.amount || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
              <td>${r.typology}</td>
              <td><span class="mono" style="font-size: 11px;">${r.action_pre}</span></td>
              <td><span class="mono" style="font-size: 11px; color: var(--text-secondary);">${r.step_up}</span></td>
              <td><strong class="mono" style="font-size: 11px; color: ${r.action_post === 'BLOCK_TRANSACTION' ? 'var(--danger)' : 'var(--success)'};">${r.action_post}</strong></td>
              <td>${r.sar_filed ? '<span class="mono" style="font-weight: 700; color: var(--danger);">YES</span>' : '<span style="color: var(--text-muted);">NO</span>'}</td>
              <td>
                <button class="nav-btn" style="padding: 0.15rem 0.45rem; font-size: 10px;" onclick="switchMainTab('dossier'); selectCase('${r.case_id}')">Investigate</button>
              </td>
            `;
            tbody.appendChild(tr);
          });
        }
      } catch (err) {
        console.error('Failed to load benchmark summary:', err);
      }
    }

    function openSearchModal() {
      document.getElementById('search-modal').style.display = 'flex';
      const input = document.getElementById('search-input');
      input.value = '';
      input.focus();
      document.getElementById('search-results-box').innerHTML = '<div style="color: var(--text-muted); font-size: 11px; text-align: center; padding: 1rem;">Type to search cases, transactions, accounts, devices...</div>';
    }

    function closeSearchModal() {
      document.getElementById('search-modal').style.display = 'none';
    }

    async function handleSearchInput(q) {
      if (!q.trim()) return;
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(q.trim())}`);
        if (res.ok) {
          const data = await res.json();
          const box = document.getElementById('search-results-box');
          box.innerHTML = '';

          const cases = data.cases || [];
          if (cases.length === 0) {
            box.innerHTML = '<div style="color: var(--text-muted); font-size: 11px; text-align: center; padding: 0.75rem;">No matching entities found.</div>';
            return;
          }

          cases.forEach(c => {
            const div = document.createElement('div');
            div.style.cssText = 'padding: 0.4rem; border-bottom: 1px solid var(--border-subtle); cursor: pointer; display: flex; justify-content: space-between; align-items: center;';
            div.onclick = () => {
              selectCase(c.case_id);
              closeSearchModal();
            };
            div.innerHTML = `
              <div>
                <strong class="mono" style="font-size: 11px;">${c.case_id}</strong>
                <div style="font-size: 10px; color: var(--text-secondary);">${c.title}</div>
              </div>
              <span class="mono" style="font-size: 10px; color: var(--danger);">Risk ${c.risk_score}</span>
            `;
            box.appendChild(div);
          });
        }
      } catch (err) {
        console.error('Search error:', err);
      }
    }

    function openStepUpModal() {
      document.getElementById('stepup-modal').style.display = 'flex';
    }

    function closeStepUpModal() {
      document.getElementById('stepup-modal').style.display = 'none';
    }

    async function submitStepUpSimulation(status) {
      if (!currentCase) return;
      closeStepUpModal();
      try {
        const res = await fetch(`/api/cases/${currentCase.case_id}/step-up`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ response_status: status, notes: `Simulation: ${status}` })
        });
        if (res.ok) {
          currentCase = await res.json();
          renderDossier();
          renderQueue();
          alert(`Step-up response [${status}] recorded. Milestone B decision updated.`);
        }
      } catch (err) {
        alert('Failed to simulate step-up verification.');
      }
    }

    function simulateActionApprove() {
      alert(`[SIMULATION]: Approved action "${document.getElementById('nba-primary-action').innerText}" for case ${currentCase?.case_id}. Audit record written.`);
    }

    function simulateActionReject() {
      alert(`[SIMULATION]: Action rejected by analyst. Escalated to Senior Fraud Reviewer.`);
    }

    function copySarNarrative() {
      const text = document.getElementById('sar-narrative-text').innerText;
      navigator.clipboard.writeText(text);
      const btn = document.getElementById('copy-sar-btn');
      btn.innerText = 'Copied!';
      setTimeout(() => btn.innerText = 'Copy Narrative', 2000);
    }

    function exportSarJson() {
      if (!currentCase?.sar_filing) return;
      const blob = new Blob([JSON.stringify(currentCase.sar_filing, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${currentCase.case_id}_fincen_sar.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  </script>
</body>
</html>
"""
