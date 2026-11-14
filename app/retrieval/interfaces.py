
from typing import Protocol, Sequence

from app.retrieval.models import Evidence


class EvidenceSource(Protocol):
    """Common interface for evidence source connectors."""

    def search(self, query: str) -> Sequence[Evidence]:
        """
        Search the source using a claim as the query.

        Args:
            query: Claim text to search for.

        Returns:
            A sequence of evidence snippets and source references.

        Raises:
            Exception: If the source cannot retrieve evidence.
        """
        ...
