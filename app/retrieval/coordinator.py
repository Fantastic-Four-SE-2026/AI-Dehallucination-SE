
import asyncio
from collections.abc import Sequence

from app.processing.claim_identifier import Claim
from app.retrieval.interfaces import EvidenceSource
from app.retrieval.models import (
    Evidence,
    RetrievalResult,
    RetrievalStatus,
)


class EvidenceRetrievalCoordinator:
    """Coordinates parallel evidence retrieval for identified claims."""

    def __init__(
        self,
        sources: Sequence[EvidenceSource],
        timeout: float = 5.0,
        max_retries: int = 1,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero.")

        if max_retries < 0:
            raise ValueError("max_retries cannot be negative.")

        self.sources = tuple(sources)
        self.timeout = timeout
        self.max_retries = max_retries

    async def _search_source(
        self,
        source: EvidenceSource,
        query: str,
    ) -> tuple[tuple[Evidence, ...], bool]:
        """Search one source with timeout and bounded retries."""

        for attempt in range(self.max_retries + 1):
            try:
                evidence = await asyncio.wait_for(
                    asyncio.to_thread(source.search, query),
                    timeout=self.timeout,
                )
                return tuple(evidence), False

            except Exception:
                if attempt == self.max_retries:
                    return (), True

        return (), True

    async def _retrieve_claim(
        self,
        claim: Claim,
    ) -> RetrievalResult:
        """Retrieve evidence from all enabled sources for one claim."""

        source_tasks = [
            self._search_source(source, claim.text)
            for source in self.sources
        ]

        source_results = await asyncio.gather(*source_tasks)

        collected_evidence = []
        failed_sources = 0

        for evidence, failed in source_results:
            collected_evidence.extend(evidence)

            if failed:
                failed_sources += 1

        if collected_evidence:
            return RetrievalResult(
                claim_id=claim.claim_id,
                request_id=claim.request_id,
                claim_text=claim.text,
                status=RetrievalStatus.SUCCESS,
                evidence=tuple(collected_evidence),
            )

        if not self.sources:
            reason = "no enabled sources"
        elif failed_sources == len(self.sources):
            reason = "retrieval failure"
        else:
            reason = "no evidence"

        return RetrievalResult(
            claim_id=claim.claim_id,
            request_id=claim.request_id,
            claim_text=claim.text,
            status=RetrievalStatus.UNCERTAIN,
            reason=reason,
        )

    async def retrieve(
        self,
        claims: Sequence[Claim],
    ) -> list[RetrievalResult]:
        """Retrieve evidence for all claims concurrently."""

        tasks = [
            self._retrieve_claim(claim)
            for claim in claims
        ]

        return await asyncio.gather(*tasks)
