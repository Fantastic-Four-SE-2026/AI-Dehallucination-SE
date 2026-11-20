
import pytest

from app.processing.claim_identifier import identify_claims


def test_each_claim_has_a_unique_id():
    claims = identify_claims(
        "Earth revolves around the Sun. Water contains hydrogen and oxygen.",
        "request_001",
    )

    claim_ids = [claim.claim_id for claim in claims]

    assert len(claim_ids) == 2
    assert len(set(claim_ids)) == 2
    assert all(claim_id.startswith("claim_") for claim_id in claim_ids)


def test_each_claim_is_linked_to_its_request():
    claims = identify_claims(
        "Earth revolves around the Sun. Water contains hydrogen and oxygen.",
        "request_123",
    )

    assert len(claims) == 2
    assert all(claim.request_id == "request_123" for claim in claims)


def test_offsets_select_exact_original_claims():
    original = (
        "Hello!  "
        "Earth   revolves around the Sun.  "
        "Water contains hydrogen and oxygen."
    )

    claims = identify_claims(original, "request_001")

    assert len(claims) == 2

    for claim in claims:
        assert (
            original[claim.start_offset:claim.end_offset]
            == claim.text
        )


def test_offsets_are_zero_based_and_end_exclusive():
    original = "Hello! Earth revolves around the Sun."

    claims = identify_claims(original, "request_002")

    assert len(claims) == 1

    claim = claims[0]

    assert claim.start_offset == 7
    assert claim.end_offset == len(original)
    assert original[claim.start_offset:claim.end_offset] == (
        "Earth revolves around the Sun."
    )

def test_offsets_remain_correct_after_unicode_preprocessing():
    original = (
        "The Sun\u2019s energy reaches Earth.  "
        "Water contains hydrogen and oxygen."
    )

    claims = identify_claims(original, "request_003")

    assert len(claims) == 2

    for claim in claims:
        assert (
            original[claim.start_offset:claim.end_offset]
            == claim.text
        )

    assert claims[0].text == "The Sun\u2019s energy reaches Earth."
def test_claims_keep_their_original_order():
    original = (
        "Earth revolves around the Sun. "
        "Water contains hydrogen and oxygen. "
        "Mars is the fourth planet from the Sun."
    )

    claims = identify_claims(original, "request_004")

    assert [claim.text for claim in claims] == [
        "Earth revolves around the Sun.",
        "Water contains hydrogen and oxygen.",
        "Mars is the fourth planet from the Sun.",
    ]


def test_empty_response_returns_no_claims():
    assert identify_claims("", "request_005") == []
    assert identify_claims("   ", "request_005") == []


def test_invalid_response_raises_type_error():
    with pytest.raises(TypeError):
        identify_claims(None, "request_006")


@pytest.mark.parametrize("request_id", ["", "   ", None, 123])
def test_invalid_request_id_raises_value_error(request_id):
    with pytest.raises(ValueError):
        identify_claims("Earth revolves around the Sun.", request_id)
