# US-010 — Factual Claim Extraction

**Story ID:** US-010
**Component:** C-06 — Claim Extractor
**SRS Requirement:** FR-05
**Status:** Implemented and tested

## 1. Purpose

Extract individual factual claims from an AI-generated response so that each claim can be checked independently by subsequent verification components.

The module identifies candidate factual statements while filtering out greetings, questions, opinions, and subjective statements.

## 2. Implementation

**Implementation file:** `app/processing/claim_extractor.py`

The module provides:

- `extract_claims()`: Accepts a text response and returns a list of candidate factual claims.
- Sentence segmentation using spaCy's English sentencizer.
- Heuristic filtering to identify candidate factual claims.
- Input validation and empty-input handling.

### Claim extraction features

1. Sentence segmentation.
2. Greeting and pleasantry filtering.
3. Question filtering.
4. Opinion and preference filtering.
5. Subjective statement filtering.
6. Handling of text containing up to 2,000 words.
7. Input validation for non-string input.

## 3. Extraction Process

1. Receive the AI-generated response.
2. Validate the input.
3. Segment the response into sentences.
4. Examine each sentence using heuristic filtering rules.
5. Exclude greetings, questions, opinions, and subjective statements.
6. Return candidate factual claims as a list.

**Note:** This component extracts candidate factual claims. It does not independently verify whether those claims are true or false.

## 4. Testing

**Test file:** `tests/test_claim_extractor.py`

Run US-010 tests:

```bash
python -m pytest -v tests/test_claim_extractor.py
