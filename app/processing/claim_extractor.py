import re

import spacy


# Initialise a lightweight English sentence splitter.
# No external language model download is required.
_nlp = spacy.blank("en")
_nlp.add_pipe("sentencizer")


# Common greetings and pleasantries.
_GREETINGS = {
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
    "good night",
    "thanks",
    "thank you",
    "thank you very much",
    "bye",
    "goodbye",
}


# Common phrases that indicate opinions or personal preferences.
_OPINION_PATTERNS = [
    r"\bi think\b",
    r"\bi believe\b",
    r"\bi feel\b",
    r"\bi guess\b",
    r"\bi suppose\b",
    r"\bin my opinion\b",
    r"\bin my view\b",
    r"\bi love\b",
    r"\bi hate\b",
    r"\bi like\b",
    r"\bi dislike\b",
    r"\bi prefer\b",
]


# Subjective terms that commonly indicate opinions.
_SUBJECTIVE_WORDS = {
    "beautiful",
    "amazing",
    "wonderful",
    "terrible",
    "fantastic",
    "boring",
    "awesome",
    "ugly",
    "worst",
}


# Words commonly used to begin questions.
_QUESTION_STARTERS = {
    "who", "what", "when", "where", "why", "which", "whose",
    "whom", "how", "is", "are", "am", "was", "were",
    "do", "does", "did", "can", "could", "would", "should",
    "will", "have", "has", "had",
}


def _is_question(sentence: str) -> bool:
    """Return True when a sentence is a question."""
    cleaned = sentence.strip()

    if "?" in cleaned:
        return True

    words = cleaned.split()
    if not words:
        return True

    first_word = re.sub(r"^[^\w]+|[^\w]+$", "", words[0]).lower()
    return first_word in _QUESTION_STARTERS


def _is_greeting(sentence: str) -> bool:
    """Return True for standalone greetings and pleasantries."""
    cleaned = sentence.strip().lower()
    cleaned = re.sub(r"[.!?,]+$", "", cleaned)
    return cleaned in _GREETINGS


def _is_opinion(sentence: str) -> bool:
    """Return True when common opinion indicators are present."""
    lowered = sentence.lower()

    for pattern in _OPINION_PATTERNS:
        if re.search(pattern, lowered):
            return True

    words = set(re.findall(r"\b[a-z]+\b", lowered))
    return bool(words.intersection(_SUBJECTIVE_WORDS))


def _is_candidate_claim(sentence: str) -> bool:
    """Filter out questions, greetings and common opinion statements."""
    if not sentence.strip():
        return False

    if _is_question(sentence):
        return False

    if _is_greeting(sentence):
        return False

    if _is_opinion(sentence):
        return False

    return True



def _extract_candidate_spans(text: str) -> list[tuple[str, int, int]]:
    """
    Extract candidate claims with their start and end positions
    in the input text. End positions are exclusive.
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")

    if not text.strip():
        return []

    doc = _nlp(text)
    claims = []

    for sentence in doc.sents:
        if not _is_candidate_claim(sentence.text):
            continue

        start = sentence.start_char
        end = sentence.end_char

        # Exclude surrounding whitespace from the claim span.
        while start < end and text[start].isspace():
            start += 1

        while end > start and text[end - 1].isspace():
            end -= 1

        if start < end:
            claims.append((text[start:end], start, end))

    return claims


def extract_claims(text: str) -> list[str]:
    """
    Extract candidate factual claims from a response.

    Preserves the existing list-of-strings interface.
    """
    return [
        claim_text
        for claim_text, _, _ in _extract_candidate_spans(text)
    ]


def extract_claim_spans(text: str) -> list[tuple[str, int, int]]:
    """
    Extract candidate factual claims with their text positions.

    Returns (claim_text, start_offset, end_offset).
    Offsets are zero-based and end-exclusive.
    """
    return _extract_candidate_spans(text)
