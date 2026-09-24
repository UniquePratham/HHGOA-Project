#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure agent-core is on Python path
repo_root = Path(__file__).resolve().parent
agent_core_dir = repo_root / "agent-core"
if str(agent_core_dir) not in sys.path:
    sys.path.insert(0, str(agent_core_dir))

if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("STARTING TIGERGRAPH AGENTIC FRAUD CONSOLE SERVER")
    print("URL: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 70)
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        app_dir=str(agent_core_dir),
    )
