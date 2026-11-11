# US-009 — Preprocessing with Position Mapping

**Story ID:** US-009  
**Jira ID:** SCRUM-25  
**Component:** C-05 — Preprocessor  
**SRS Requirement:** FR-04  
**Priority:** High  
**Story Points:** 5  
**Status:** Implemented and tested

## 1. Purpose

Normalize input text while preserving the original text and maintaining a mapping from positions in the cleaned text back to their corresponding positions in the original text.

This ensures that claim offsets can be traced back to the original AI-generated response.

## 2. Implementation

**Implementation file:** `app/processing/preprocessor.py`

The module provides:

- `PreprocessingResult`: Stores the original text, cleaned text, and position mapping.
- `preprocess_text()`: Performs text preprocessing.
- `map_position()`: Maps a cleaned-text character position to its original starting position.
- `map_span()`: Maps a cleaned-text span to its corresponding original-text span.

### Preprocessing features

1. **Whitespace normalization:** Collapses consecutive whitespace and removes leading and trailing whitespace.
2. **Symbol normalization:** Normalizes supported curly quotation marks, long dashes, and ellipsis symbols.
3. **Unicode normalization:** Applies Unicode NFC normalization to supported character sequences.
4. **Position mapping:** Maintains original position ranges for every character in the cleaned text.
5. **Original text preservation:** Keeps the original input unchanged in the result.

## 3. Position Mapping

Each character in the cleaned text has a corresponding range in the original text.

The mapping supports:

- Individual character position lookup.
- Mapping of cleaned-text spans using zero-based, end-exclusive offsets.
- Handling of normalized symbols and collapsed whitespace.
- Validation of invalid positions and spans.

## 4. Testing

**Test file:** `tests/test_preprocessor.py`

Run the tests from the project root:

```powershell
python -m pytest -v
```

**Latest test result: 18 passed, 0 failed.**

Test coverage includes:

- Whitespace normalization.
- Symbol normalization.
- Character and span position mapping.
- Original text preservation.
- Empty input.
- Leading and trailing whitespace.
- Multiple newlines and tabs.
- Unicode text preservation and NFC normalization.
- Ellipsis and collapsed whitespace mapping.
- Invalid positions, spans, and input types.
- Mapping boundary validation.

## 5. Acceptance Criteria

| Acceptance criterion | Result |
|---|---|
| Extra whitespace and symbols are normalized | Passed |
| Any valid position in cleaned text maps back to the original | Passed |
| Original text remains unchanged | Passed |

## 6. Result

US-009 implementation is completed. All 18 preprocessing tests passed successfully.

The C-05 Preprocessor is ready for integration with the C-06 Claim Extractor.