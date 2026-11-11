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


def extract_claims(text: str) -> list[str]:
    """
    Extract candidate factual claims from a response.

    Uses spaCy for sentence segmentation and heuristic rules
    to filter questions, greetings and common opinion statements.

    This function identifies candidate claims; it does not
    determine whether those claims are factually true.
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")

    if not text.strip():
        return []

    doc = _nlp(text)

    return [
        sentence.text.strip()
        for sentence in doc.sents
        if _is_candidate_claim(sentence.text)
    ]
