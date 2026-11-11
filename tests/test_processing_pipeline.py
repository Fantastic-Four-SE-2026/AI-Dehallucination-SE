
from app.processing.claim_identifier import identify_claims


def test_complete_processing_pipeline():
    response = (
        "Hello!  The Earth is round.  "
        "The Earth revolves around the Sun. "
        "I think Python is amazing. "
        "Water freezes at 0°C."
    )

    claims = identify_claims(
        original_response=response,
        request_id="request_001",
    )

    expected_claims = [
        "The Earth is round.",
        "The Earth revolves around the Sun.",
        "Water freezes at 0°C.",
    ]

    assert len(claims) == 3

    for claim, expected_text in zip(claims, expected_claims):
        assert claim.text == expected_text
        assert claim.request_id == "request_001"

        # Verify exact original-response offsets.
        assert response[
            claim.start_offset:claim.end_offset
        ] == expected_text


def test_pipeline_preserves_unicode_and_whitespace():
    response = (
        "The student’s name is José.   "
        "The temperature is 25°C."
    )

    claims = identify_claims(
        original_response=response,
        request_id="request_002",
    )

    assert len(claims) == 2

    for claim in claims:
        assert response[
            claim.start_offset:claim.end_offset
        ] == claim.text


def test_pipeline_generates_unique_claim_ids():
    response = (
        "The Earth is round. "
        "Mars is a planet."
    )

    claims = identify_claims(response, "request_003")

    claim_ids = [claim.claim_id for claim in claims]

    assert len(claim_ids) == len(set(claim_ids))


def test_pipeline_handles_empty_response():
    claims = identify_claims("", "request_004")

    assert claims == []
