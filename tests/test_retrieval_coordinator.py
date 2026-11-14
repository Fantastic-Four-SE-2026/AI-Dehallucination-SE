
import asyncio
import time

import pytest

from app.processing.claim_identifier import Claim
from app.retrieval.coordinator import EvidenceRetrievalCoordinator
from app.retrieval.models import (
    Evidence,
    RetrievalStatus,
)


class MockSource:
    def __init__(self, evidence=None, error=None, delay=0):
        self.evidence = evidence or []
        self.error = error
        self.delay = delay
        self.calls = []

    def search(self, query):
        self.calls.append(query)

        if self.delay:
            time.sleep(self.delay)

        if self.error:
            raise self.error

        return self.evidence


def make_claim(claim_id, text):
    return Claim(
        claim_id=claim_id,
        request_id="request_001",
        text=text,
        start_offset=0,
        end_offset=len(text),
    )


@pytest.mark.asyncio
async def test_one_query_per_claim():
    source = MockSource(
        evidence=[
            Evidence(
                snippet="Bengaluru is the capital of Karnataka.",
                source="MockSource",
                reference="https://example.com",
            )
        ]
    )

    claims = [
        make_claim("claim_1", "Bengaluru is the capital of Karnataka."),
        make_claim("claim_2", "The Earth revolves around the Sun."),
    ]

    coordinator = EvidenceRetrievalCoordinator([source])

    results = await coordinator.retrieve(claims)

    assert len(results) == 2
    assert source.calls == [claim.text for claim in claims]


@pytest.mark.asyncio
async def test_successful_evidence_retrieval():
    evidence = Evidence(
        snippet="Bengaluru is the capital of Karnataka.",
        source="MockSource",
        reference="https://example.com",
    )

    source = MockSource(evidence=[evidence])

    claim = make_claim(
        "claim_1",
        "Bengaluru is the capital of Karnataka.",
    )

    coordinator = EvidenceRetrievalCoordinator([source])

    results = await coordinator.retrieve([claim])

    assert results[0].status == RetrievalStatus.SUCCESS
    assert results[0].evidence == (evidence,)
    assert results[0].reason is None


@pytest.mark.asyncio
async def test_empty_results_return_uncertain():
    source = MockSource(evidence=[])

    claim = make_claim("claim_1", "Unknown factual statement.")

    coordinator = EvidenceRetrievalCoordinator([source])

    results = await coordinator.retrieve([claim])

    assert results[0].status == RetrievalStatus.UNCERTAIN
    assert results[0].reason == "no evidence"
    assert source.calls == [claim.text]


@pytest.mark.asyncio
async def test_source_failure_retries_once():
    source = MockSource(error=RuntimeError("HTTP 503"))

    claim = make_claim("claim_1", "Test claim.")

    coordinator = EvidenceRetrievalCoordinator(
        [source],
        max_retries=1,
    )

    results = await coordinator.retrieve([claim])

    assert results[0].status == RetrievalStatus.UNCERTAIN
    assert results[0].reason == "retrieval failure"
    assert source.calls == [claim.text, claim.text]


@pytest.mark.asyncio
async def test_disabled_sources_are_not_called():
    enabled_source = MockSource(
        evidence=[
            Evidence(
                snippet="Evidence found.",
                source="EnabledSource",
                reference="https://example.com",
            )
        ]
    )

    disabled_source = MockSource(
        evidence=[
            Evidence(
                snippet="Should not be retrieved.",
                source="DisabledSource",
                reference="https://disabled.example.com",
            )
        ]
    )

    # Only enabled connectors are passed to the coordinator.
    coordinator = EvidenceRetrievalCoordinator([enabled_source])

    claim = make_claim("claim_1", "Test claim.")

    await coordinator.retrieve([claim])

    assert enabled_source.calls == [claim.text]
    assert disabled_source.calls == []


@pytest.mark.asyncio
async def test_source_timeout_retries_once():
    source = MockSource(delay=0.2)

    claim = make_claim("claim_1", "Test claim.")

    coordinator = EvidenceRetrievalCoordinator(
        [source],
        timeout=0.05,
        max_retries=1,
    )

    results = await coordinator.retrieve([claim])

    assert results[0].status == RetrievalStatus.UNCERTAIN
    assert results[0].reason == "retrieval failure"
    assert source.calls == [claim.text, claim.text]


@pytest.mark.asyncio
async def test_claims_are_processed_in_parallel():
    source = MockSource(
        evidence=[
            Evidence(
                snippet="Evidence found.",
                source="MockSource",
                reference="https://example.com",
            )
        ],
        delay=0.3,
    )

    claims = [
        make_claim("claim_1", "First claim."),
        make_claim("claim_2", "Second claim."),
    ]

    coordinator = EvidenceRetrievalCoordinator([source])

    start = time.perf_counter()
    results = await coordinator.retrieve(claims)
    elapsed = time.perf_counter() - start

    assert len(results) == 2
    assert all(
        result.status == RetrievalStatus.SUCCESS
        for result in results
    )
    assert elapsed < 0.55


@pytest.mark.asyncio
async def test_sources_are_processed_in_parallel():
    evidence_1 = Evidence(
        snippet="Evidence from source 1.",
        source="Source1",
        reference="https://source1.example.com",
    )

    evidence_2 = Evidence(
        snippet="Evidence from source 2.",
        source="Source2",
        reference="https://source2.example.com",
    )

    source_1 = MockSource(evidence=[evidence_1], delay=0.3)
    source_2 = MockSource(evidence=[evidence_2], delay=0.3)

    claim = make_claim("claim_1", "Test factual claim.")

    coordinator = EvidenceRetrievalCoordinator(
        [source_1, source_2]
    )

    start = time.perf_counter()
    results = await coordinator.retrieve([claim])
    elapsed = time.perf_counter() - start

    assert results[0].status == RetrievalStatus.SUCCESS
    assert len(results[0].evidence) == 2
    assert source_1.calls == [claim.text]
    assert source_2.calls == [claim.text]
    assert elapsed < 0.55

@pytest.mark.asyncio
async def test_no_enabled_sources_returns_uncertain():
    claim = make_claim("claim_1", "Test claim.")

    coordinator = EvidenceRetrievalCoordinator([])

    results = await coordinator.retrieve([claim])

    assert results[0].status == RetrievalStatus.UNCERTAIN
    assert results[0].reason == "no enabled sources"
