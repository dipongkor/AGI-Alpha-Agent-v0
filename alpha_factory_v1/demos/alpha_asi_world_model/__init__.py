# SPDX-License-Identifier: Apache-2.0
"""
╭──────────────────────────────────────────────────────────────────────────────╮
│  Alpha-Factory v1 👁️✨ — Multi-Agent AGENTIC α-AGI World-Model Demo          │
│  ░░  “Outlearn · Outthink · Outdesign · Outstrategize · Outexecute”  ░░      │
│                                                                              │
│  This package exposes a *single-import* interface to the fully-agentic       │
│  α-ASI demonstrator implemented in `alpha_asi_world_model_demo.py`.          │
│                                                                              │
│  Highlights                                                                  │
│  ───────────────────────────────────────────────────────────────────────────  │
│  • Five complementary agents (**planner, researcher, strategist, market,     │
│    safety**) auto-register on import, showcasing the Alpha-Factory pattern   │
│    of end-to-end Alpha discovery → execution across industries.              │
│  • One-liner launch helpers for notebooks & scripts                          │
│      >>> import alpha_asi_world_model as α                                   │
│      >>> α.run_ui(port=9999)   # open http://localhost:9999                  │
│  • Zero mandatory cloud keys – runs fully offline; plugs-in GPT/Claude et al │
│    automatically *if* `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` are present.    │
│  • Strict, regulator-friendly defaults: deterministic seed, telemetry opt-in │
│    only, graceful exit on NaN / divergence (SafetyAgent).                    │
╰──────────────────────────────────────────────────────────────────────────────╯
The ``__version__`` constant below denotes the demo revision and is
independent from the :mod:`alpha_factory_v1` package version.
"""

from __future__ import annotations

import importlib
import os
import threading
from types import ModuleType
from typing import Final, List

# Re-export the runnable demo components
try:  # optional heavy deps (numpy, torch, etc.)
    from .alpha_asi_world_model_demo import (  # noqa: F401
        CFG,
        TORCH_AVAILABLE,
        Orchestrator,
        _main as _demo_cli,
        app,
    )

    _DEPS_AVAILABLE = bool(TORCH_AVAILABLE)
except Exception:  # pragma: no cover - missing optional deps
    CFG = Orchestrator = app = _demo_cli = None  # type: ignore
    TORCH_AVAILABLE = False
    _DEPS_AVAILABLE = False

__all__: Final[List[str]] = [
    "Orchestrator",
    "run_headless",
    "run_ui",
    "app",
    "__version__",
]

__version__: Final[str] = "1.1.0"

# ──────────────────────────────────────────────────────────────────────────────
#  Agent showcase (edu-doc string for auditors & newcomers)
# ──────────────────────────────────────────────────────────────────────────────
Agent_DOC = """
Integrated Alpha-Factory agents (auto-stubbed if source class unavailable):

• PlanningAgent       – decomposes high-level objectives into actionable plans  
• ResearchAgent       – scans literature / data sources → distilled insights  
• StrategyAgent       – converts insights into cross-industry competitive moves  
• MarketAnalysisAgent – evaluates financial / market impact of candidate moves  
• SafetyAgent         – continuous risk/constraint monitor; halts on anomaly

Together they demonstrate the ‘Alpha Pipeline’:
   *Detect → Research → Strategise → Execute → Monitor/Safeguard*.
"""


# ──────────────────────────────────────────────────────────────────────────────
#  Convenience helpers
# ──────────────────────────────────────────────────────────────────────────────
def _lazy_import_uvicorn() -> ModuleType:  # local import keeps deps optional
    return importlib.import_module("uvicorn")


def run_headless(steps: int = 50_000) -> Orchestrator:  # pragma: no cover
    """
    Launch the orchestrator loop **without** spinning up the FastAPI service.

    Useful for Jupyter / unit-tests:

        >>> import alpha_asi_world_model as α
        >>> orch = α.run_headless(10_000)
        >>> assert orch.learner.buffer  # trained a bit
    """
    if not _DEPS_AVAILABLE:
        raise ImportError("Optional dependencies missing; install requirements.txt to run")

    orch = Orchestrator()

    CFG.max_steps = steps

    def _worker() -> None:
        orch.loop()

    threading.Thread(target=_worker, daemon=True).start()
    return orch


def run_ui(
    host: str = "127.0.0.1",
    port: int = 7860,
    reload: bool = False,
    log_level: str = "info",
) -> None:  # pragma: no cover
    """
    Spin up the FastAPI REST + WebSocket UI.

        >>> import alpha_asi_world_model as α
        >>> α.run_ui(port=9999)  # then open http://localhost:9999
    """
    if not _DEPS_AVAILABLE:
        raise ImportError("Optional dependencies missing; install requirements.txt to run")

    uvicorn = _lazy_import_uvicorn()
    uvicorn.run(
        "alpha_factory_v1.demos.alpha_asi_world_model.alpha_asi_world_model_demo:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


# ──────────────────────────────────────────────────────────────────────────────
#  Informative banner (prints once on first import, unless suppressed)
# ──────────────────────────────────────────────────────────────────────────────
if os.getenv("ALPHA_ASI_SILENT", "0") != "1":
    print(
        f"\n💡  Alpha-ASI demo ready — version {__version__} • "
        "type `help(alpha_asi_world_model)` for details - or - "
        "`alpha_asi_world_model.run_ui()` to launch the dashboard.\n"
    )


# Expose a CLI entry-point (python -m alpha_asi_world_model)
def _module_cli() -> None:  # pragma: no cover
    """Dispatch to the demo’s CLI (see `alpha_asi_world_model_demo --help`)."""
    _demo_cli()


if __name__ == "__main__":  # allows:  python -m alpha_asi_world_model …
    _module_cli()
