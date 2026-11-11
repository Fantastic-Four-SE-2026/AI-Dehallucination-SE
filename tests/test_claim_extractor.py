import pytest

from app.processing.claim_extractor import extract_claims


def test_extract_three_factual_claims():
    text = (
        "Earth revolves around the Sun. "
        "Water boils at 100 degrees Celsius at standard atmospheric pressure. "
        "The human heart pumps blood throughout the body."
    )

    claims = extract_claims(text)

    assert len(claims) == 3
    assert claims[0] == "Earth revolves around the Sun."
    assert claims[1] == (
        "Water boils at 100 degrees Celsius at standard atmospheric pressure."
    )
    assert claims[2] == "The human heart pumps blood throughout the body."


def test_ignore_questions():
    text = (
        "The Earth revolves around the Sun. "
        "Is the Earth round? "
        "Water contains hydrogen and oxygen."
    )

    claims = extract_claims(text)

    assert len(claims) == 2
    assert all("?" not in claim for claim in claims)


def test_ignore_greetings():
    text = (
        "Hello! "
        "The Sun is a star. "
        "Good morning! "
        "Water is a chemical compound."
    )

    claims = extract_claims(text)

    assert len(claims) == 2
    assert "The Sun is a star." in claims
    assert "Water is a chemical compound." in claims


def test_ignore_opinions():
    text = (
        "I think Python is the best programming language. "
        "Python was first released in 1991. "
        "In my opinion, mathematics is beautiful."
    )

    claims = extract_claims(text)

    assert len(claims) == 1
    assert claims[0] == "Python was first released in 1991."


def test_mixed_input():
    text = (
        "Hello! "
        "The Moon orbits the Earth. "
        "What is the Moon? "
        "I believe space exploration is amazing. "
        "Mars is the fourth planet from the Sun."
    )

    claims = extract_claims(text)

    assert len(claims) == 2
    assert claims[0] == "The Moon orbits the Earth."
    assert claims[1] == "Mars is the fourth planet from the Sun."


def test_handle_2000_word_text():
    sentence = "Earth revolves around the Sun."
    text = " ".join([sentence] * 2000)

    claims = extract_claims(text)

    assert len(claims) == 2000


def test_empty_input():
    assert extract_claims("") == []
    assert extract_claims("   ") == []


def test_invalid_input():
    with pytest.raises(TypeError):
        extract_claims(None)
