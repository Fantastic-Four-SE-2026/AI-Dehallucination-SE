from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    """Evidence retrieved from a trusted source."""

    snippet: str
    source: str
    reference: str