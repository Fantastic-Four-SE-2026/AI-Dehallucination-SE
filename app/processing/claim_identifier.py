
from dataclasses import dataclass
from uuid import uuid4

from app.processing.claim_extractor import extract_claim_spans
from app.processing.preprocessor import preprocess_text


@dataclass(frozen=True)
class Claim:
    """A candidate claim linked to its original request and response."""

    claim_id: str
    request_id: str
    text: str
    start_offset: int
    end_offset: int


def identify_claims(
    original_response: str,
    request_id: str,
) -> list[Claim]:
    """
    Extract claims and assign IDs and original-response offsets.

    Offsets are zero-based and end-exclusive.
    Claim text is the exact substring from the original response.
    """
    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("request_id must be a non-empty string.")

    # Preprocess while retaining positions in the original response.
    preprocessing_result = preprocess_text(original_response)
    cleaned_text = preprocessing_result.cleaned_text

    # Extract candidate claims and their cleaned-text positions.
    candidate_spans = extract_claim_spans(cleaned_text)

    claims = []

    for _, cleaned_start, cleaned_end in candidate_spans:
        # Convert cleaned-text positions into original-response positions.
        original_start, original_end = preprocessing_result.map_span(
            cleaned_start,
            cleaned_end,
        )

        # Preserve the exact original substring.
        original_claim_text = original_response[
            original_start:original_end
        ]

        claims.append(
            Claim(
                claim_id=f"claim_{uuid4().hex}",
                request_id=request_id,
                text=original_claim_text,
                start_offset=original_start,
                end_offset=original_end,
            )
        )

    return claims
