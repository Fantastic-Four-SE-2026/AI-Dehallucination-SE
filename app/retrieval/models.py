
from dataclasses import dataclass, field
from enum import Enum


class RetrievalStatus(str, Enum):
    """Status of evidence retrieval for a claim."""

    SUCCESS = "Success"
    UNCERTAIN = "Uncertain"


@dataclass(frozen=True)
class Evidence:
    """Evidence retrieved from a trusted source."""

    snippet: str
    source: str
    reference: str


@dataclass(frozen=True)
class RetrievalResult:
    """Evidence retrieval outcome for an individual claim."""

    claim_id: str
    request_id: str
    claim_text: str
    status: RetrievalStatus
    evidence: tuple[Evidence, ...] = field(default_factory=tuple)
    reason: str | None = None
