# US-009 â€” Preprocessing with Position Mapping



**Story:** US-009

**Component:** C-05 â€” Preprocessor

**Requirement:** FR-04



## Purpose



Normalize whitespace while preserving the original text and mapping positions in the cleaned text back to the original text.



## Implementation



\- `app/processing/preprocessor.py`

\- `PreprocessingResult` stores the original text, cleaned text, and position map.

\- `preprocess_text()` collapses repeated whitespace and removes leading and trailing whitespace.

\- `map_span_to_original()` maps cleaned-text spans to original-text offsets.



## Tests



Test file: `tests/test_preprocessor.py`



Run from the repository root:



`python -m unittest discover -s tests -v`



Six tests have passed locally.



## Scope Note



The current implementation handles whitespace normalization. Symbol normalization and additional position-mapping edge cases still need validation before all US-009 acceptance criteria can be considered complete.
