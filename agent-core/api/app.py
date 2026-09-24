from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure agent-core directory is on sys.path
_core_dir = Path(__file__).resolve().parent.parent
if str(_core_dir) not in sys.path:
    sys.path.insert(0, str(_core_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api.routes import router
from api.static_console import CONSOLE_HTML

app = FastAPI(
    title="TigerGraph Agentic Fraud Investigation API",
    description="Backend service powering the HHGOA Hackathon Agentic Fraud & Next-Best Action Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
def root_console():
    return CONSOLE_HTML


@app.get("/console", response_class=HTMLResponse)
def console_view():
    return CONSOLE_HTML


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("api.app:app", host=host, port=port, reload=True)
