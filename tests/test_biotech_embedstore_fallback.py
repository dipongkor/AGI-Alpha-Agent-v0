# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import importlib

import pytest


@pytest.mark.asyncio
async def test_embedstore_faiss_free_search_uses_query_terms(monkeypatch: pytest.MonkeyPatch) -> None:
    biotech_agent = importlib.import_module("alpha_factory_v1.backend.agents.biotech_agent")
    monkeypatch.setattr(biotech_agent, "faiss", None)
    store = biotech_agent._EmbedStore(biotech_agent.BTConfig())
    await store.add(
        ["EGFR inhibitor response in lung cancer", "Maize irrigation optimization"],
        ["pmid:1", "pmid:2"],
    )

    hits = await store.search("egfr cancer", k=5)
    assert hits == [("EGFR inhibitor response in lung cancer", "pmid:1", 2.0)]


@pytest.mark.asyncio
async def test_embedstore_faiss_free_search_returns_empty_when_no_match(monkeypatch: pytest.MonkeyPatch) -> None:
    biotech_agent = importlib.import_module("alpha_factory_v1.backend.agents.biotech_agent")
    monkeypatch.setattr(biotech_agent, "faiss", None)
    store = biotech_agent._EmbedStore(biotech_agent.BTConfig())
    await store.add(["Cloud storage pricing"], ["doc:1"])

    assert await store.search("oncology pathway") == []
