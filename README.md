# TigerGraph Agentic Fraud Investigation & Next-Best Action Platform

> **HHGOA Hackathon Submission** — Autonomous fraud investigation agent powered by TigerGraph graph traversal, deterministic GraphRAG reasoning, dual-stage Next-Best Action decisions, and FinCEN SAR narrative generation.

---

## What This System Does

A financial transaction triggers a fraud signal. This platform:

1. **Ingests** the trigger and registers a case.
2. **Traverses** a 2-hop ego-network around the suspect transaction in TigerGraph, extracting device clusters, IP neighborhoods, card velocity rings, and merchant patterns.
3. **Extracts evidence** partitioned as Observed Facts, Inferences, and Recommendations — each grounded to specific GSQL traversal outputs.
4. **Assesses uncertainty** via an Information Completeness Index (ICI), identifying exactly which signals remain unverified.
5. **Commits Milestone A** — a pre-evidence Next-Best Action with defensibility rationale and approval routing.
6. **Simulates a step-up challenge** (SMS OTP, biometric push, cardholder callback) to inject secondary evidence.
7. **Commits Milestone B** — a post-evidence NBA dynamically recalculated based on the step-up outcome.
8. **Generates a FinCEN SAR narrative** for cases that cross regulatory thresholds.
9. **Writes findings back** to TigerGraph as case memory for future investigations.

All 20 benchmark cases run through this full pipeline with deterministic, reproducible outputs.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Analyst Workbench                      │
│  ┌──────────┐  ┌────────────────────┐  ┌─────────────┐  │
│  │  Queue    │  │ Investigation      │  │ Graph +     │  │
│  │  220px    │  │ Dossier (Center)   │  │ Inspector   │  │
│  │  Filter   │  │ Trigger → Timeline │  │ Ego-Net     │  │
│  │  Status   │  │ Evidence → NBA     │  │ Node Click  │  │
│  │  Select   │  │ Assessment → SAR   │  │ Case Memory │  │
│  └──────────┘  └────────────────────┘  └─────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────┴──────────────────────────────────┐
│                  FastAPI Backend (8000)                   │
│  /api/cases · /api/investigate · /api/search             │
│  /api/cases/{id}/step-up · /api/benchmark/summary        │
│  /api/cases/{id}/print · /api/graph/{id}/ego             │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│             Agentic Investigation Orchestrator            │
│  8-Stage State Machine · Evidence Extraction             │
│  Uncertainty Engine · Dual NBA · SAR Generator           │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────┐
│             TigerGraph Knowledge Graph Layer              │
│  Ego-Net Traversal · Shared-Device Ring Detection        │
│  Transaction Velocity Cycles · Case Memory Cosine        │
│  Schema: User, Account, Card, Transaction, Device, IP,   │
│          Merchant, EmailDomain, Case                     │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Graph Database | TigerGraph (Savanna / Community Edition via GSQL REST) |
| Backend API | Python 3.11+, FastAPI, Pydantic v2 |
| Graph Algorithms | NetworkX (fixture mode), GSQL (live mode) |
| Frontend | Embedded HTML/CSS/JS workbench + Next.js 14 console |
| Reasoning | Deterministic GraphRAG — no hallucination, every claim grounded |
| ML Features | scikit-learn (cosine similarity for case memory), numpy, pandas |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for the Next.js web console)
- pip

### 1. Clone and Install

```bash
git clone https://github.com/YOUR_USERNAME/hhgoa-tigergraph-fraud.git
cd hhgoa-tigergraph-fraud

# Python dependencies
pip install -r agent-core/requirements.txt

# (Optional) Next.js console
cd web-console && npm install && cd ..
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your TigerGraph credentials
# Default: GRAPH_GATEWAY_MODE=fixture (no TigerGraph instance required)
```

### 3. Run the Server

```bash
python run_server.py
```

Open **http://localhost:8000** for the integrated investigation workbench.

### 4. Run Tests

```bash
python -m pytest -v
# Expected: 20 passed
```

### 5. (Optional) Run the Next.js Console

```bash
cd web-console
npm run dev
# Opens at http://localhost:3000
```

---

## Gateway Modes

| Mode | Description | Requirements |
|------|------------|-------------|
| `fixture` (default) | High-fidelity in-memory graph engine with IEEE-CIS dataset patterns. Full subgraph traversal, Louvain clustering, cycle detection, cosine similarity. | None — runs locally |
| `live` | Connects to TigerGraph Savanna or Community edition via GSQL REST endpoints. | TigerGraph instance + credentials in `.env` |

Set via `GRAPH_GATEWAY_MODE` in `.env`.

---

## Benchmark: 20 Official Cases

Located at [`cases/HHG-001.json`](cases/HHG-001.json) through [`cases/HHG-020.json`](cases/HHG-020.json).

Each case file contains the complete investigation record:

| Field | Description |
|-------|------------|
| `case_id` | Unique investigation identifier |
| `investigation_record` | Full trigger, timeline, evidence, uncertainty assessment |
| `evidence_gathered` | Partitioned: Observed Facts, Inferences, Recommendations |
| `findings` | Matched typology, risk score, graph indicators |
| `decisions_and_actions_taken` | Dual-stage NBA with defensibility rationale |
| `written_to_graph` | Graph write-back confirmation |
| `graph_write_back_details` | Target graph, node/edge counts, timestamp |
| `suspicious_activity_report` | FinCEN SAR narrative (when applicable) |
| `next_best_action_before_additional_evidence` | Milestone A decision |
| `next_best_action_after_additional_evidence` | Milestone B decision |

### Fraud Typologies Covered

1. **Account Takeover (ATO)** — new device/IP, credential changes, velocity burst
2. **Card Testing / Spinning** — micro-transactions followed by high-ticket attempts
3. **Synthetic Identity** — shared SSN fragments, name mismatches, new accounts
4. **Velocity Mule Rings** — circular transfers, smurfing, multi-account routing
5. **Merchant Collusion** — concentrated chargebacks, repetitive patterns

---

## API Reference

| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/api/health` | Service health and active case count |
| `POST` | `/api/investigate` | Run full investigation on a transaction |
| `GET` | `/api/cases` | List all investigated cases |
| `GET` | `/api/cases/{id}` | Get full case dossier |
| `POST` | `/api/cases/{id}/step-up` | Inject secondary evidence response |
| `GET` | `/api/cases/{id}/print` | Printable forensic report payload |
| `GET` | `/api/graph/{node_id}/ego` | Ego-network subgraph extraction |
| `GET` | `/api/search?q=` | Multi-entity global search |
| `GET` | `/api/benchmark/cases` | Raw benchmark case specifications |
| `GET` | `/api/benchmark/summary` | Aggregated benchmark evaluation |

Interactive API docs: **http://localhost:8000/docs**

---

## Investigation Workbench

The frontend is a 3-pane forensic workbench:

- **Left (220px)**: Filterable investigation queue with status indicators
- **Center**: Full case dossier — trigger narrative, chronological timeline, structured evidence record, uncertainty assessment, dual-stage NBA panel, FinCEN SAR draft
- **Right (310px)**: High-DPI ego-net graph canvas with click-to-inspect node inspector and case memory precedents

Features:
- Dark/Light theme toggle
- Ctrl+K global entity search
- Step-up verification simulation modal
- SAR narrative copy and JSON export
- Print-optimized layout (Ctrl+P)
- Responsive breakpoints for tablet/mobile

---

## Project Structure

```
├── agent-core/
│   ├── agent/           # Investigation orchestrator (8-stage state machine)
│   ├── api/             # FastAPI routes, static workbench HTML
│   ├── benchmark/       # 20 case specs, evaluator, answer file builder
│   ├── graph/           # TigerGraph gateway (live + fixture modes)
│   ├── knowledge/       # GraphRAG policy KB, fraud typologies
│   ├── models/          # Pydantic models (case, evidence, actions, entities)
│   ├── tests/           # Unit + integration tests
│   └── requirements.txt
├── cases/               # 20 benchmark JSON deliverables (HHG-001..HHG-020)
├── tests/               # End-to-end pipeline tests
├── web-console/         # Next.js 14 forensic command center (Vercel-ready)
├── vercel.json          # One-click Vercel deployment config
├── run_server.py        # Server entry point
├── .env.example         # Environment template
└── pytest.ini           # Test configuration
```

---

## Vercel Deployment

The web console is completely Vercel-ready and can be deployed with zero additional configuration:

1. Import this repository in [Vercel](https://vercel.com).
2. The root `vercel.json` automatically configures the Next.js build.
3. (Optional) Set `BACKEND_URL` to point to a deployed FastAPI instance, or leave unset to use the bundled benchmark dataset with real-time interactive step-up simulation.
4. Deploy!

---

## Key Design Decisions

1. **Deterministic GraphRAG over LLM generation**: Every evidence claim traces to a specific GSQL traversal output. No hallucinated fraud narratives.
2. **Dual-stage NBA**: Milestone A (pre-evidence) and B (post-evidence) are independently committed with policy citations, enabling audit trails.
3. **Fixture gateway parity**: The offline engine replicates TigerGraph GSQL semantics faithfully enough to produce benchmark-grade results without a live instance.
4. **Evidence partitioning**: Strict separation of Observed Facts (graph data), Inferences (agent reasoning), and Recommendations (policy-based actions) ensures regulatory defensibility.
5. **Uncertainty-first design**: The Information Completeness Index (ICI) explicitly quantifies what the agent knows versus what it doesn't, driving step-up decisions.

---

## License

MIT

---

## Team

**HHGOA Team** — Built for the TigerGraph Graph + AI Hackathon
