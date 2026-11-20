# US-011: Claim IDs and Start/End Offsets

## 1. Overview

**User Story ID:** US-011  
**Title:** Claim IDs and Start/End Offsets  
**Component:** C-06 - Claim Extraction and Identification  
**Status:** Implemented

This user story assigns a unique identifier to every factual claim extracted from an AI-generated response. It also records the original text and its start and end character offsets so that each claim can be traced back to its exact location in the original response.

## 2. Objective

The objective is to provide uniquely identifiable claims with accurate positional information. These identifiers and offsets allow subsequent components to retrieve evidence, verify individual claims, and report verification results against the original response.

## 3. Input

The claim identification module accepts:

- **original_response:** The complete AI-generated response.
- **request_id:** A unique identifier associated with the original request.

## 4. Output

For every identified factual claim, the module generates a `Claim` object containing:

| Field | Description |
|---|---|
| `claim_id` | Unique identifier assigned to the claim. |
| `request_id` | Identifier of the request associated with the response. |
| `text` | Exact claim text from the original response. |
| `start_offset` | Starting character position in the original response. |
| `end_offset` | Ending character position in the original response (exclusive). |

## 5. Implementation

The functionality is implemented in:

`app/processing/claim_identifier.py`

The module uses the existing preprocessing and claim extraction components.

### Processing Steps

1. Accept the original AI-generated response and request ID.
2. Preprocess the response using the US-009 preprocessing component.
3. Extract factual claim spans using the US-010 claim extraction component.
4. Map the extracted positions from the cleaned text back to the original response.
5. Retrieve the exact claim text using the original character offsets.
6. Generate a unique claim ID for each extracted claim.
7. Return the identified claims as `Claim` objects.

### Main Functions and Data Structure

- `Claim`: Frozen data class representing an identified claim.
- `identify_claims(original_response, request_id)`: Identifies claims and assigns unique IDs and original-text offsets.

## 6. Integration with Previous User Stories

- **US-009 - Preprocessing with Position Mapping:** Provides cleaned text and position mapping to preserve the relationship between processed text and the original response.
- **US-010 - Extract Factual Claims:** Identifies factual claims and their spans in the preprocessed text.
- **US-011 - Claim IDs and Start/End Offsets:** Assigns unique identifiers and maps claim positions back to the original response.

## 7. Testing

The implementation is tested using:

- `tests/test_claim_identifier.py`
- `tests/test_processing_pipeline.py`

The tests cover:

- Unique claim ID generation.
- Request ID association.
- Correct claim text extraction.
- Accurate start and end offsets.
- Mapping offsets back to the original response.
- Handling multiple extracted claims.
- Integration with preprocessing and claim extraction.
- Invalid request ID handling.

The complete project test suite was executed successfully:

**42 tests passed.**

## 8. Expected Outcome

Each extracted factual claim has a unique identifier and accurate start and end offsets referring to the original AI-generated response. This enables downstream verification components to process claims independently while retaining traceability to the original response.