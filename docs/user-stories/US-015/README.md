# US-015: Wikidata Evidence Connector

## 1. Overview

**User Story ID:** US-015  
**Title:** Wikidata Evidence Connector  
**Component:** C-08 - Evidence Retrieval  
**Status:** Implemented

This user story implements a Wikidata connector that retrieves structured factual information from Wikidata and converts the retrieved information into standardized Evidence objects.

The connector provides factual evidence and source references that can be used by downstream verification components.

## 2. Objective

The objective is to retrieve relevant factual evidence from Wikidata using a search query.

The connector searches for matching entities, retrieves their structured claims, resolves property and linked-entity labels, and generates readable evidence snippets with references to the original Wikidata entities.

## 3. Input

The connector accepts:

- **query:** A string containing the subject or entity to search for.

The connector also supports configurable initialization parameters:

| Parameter | Description | Default |
|---|---|---|
| `timeout` | Maximum time allowed for an API request, in seconds. | 5.0 |
| `limit` | Maximum number of search entities to retrieve. | 5 |
| `max_evidence` | Maximum number of evidence objects returned. | 20 |
| `user_agent` | User-Agent header sent with API requests. | AI-Dehallucination-Project/1.0 |

## 4. Output

The connector returns a list of `Evidence` objects.

Each Evidence object contains:

| Field | Description |
|---|---|
| `snippet` | Readable factual information retrieved from Wikidata. |
| `source` | Name of the evidence source, set to `Wikidata`. |
| `reference` | URL of the corresponding Wikidata entity. |

The Evidence model is an immutable data class shared with other retrieval components.

## 5. Implementation

The functionality is implemented in:

`app/retrieval/wikidata_connector.py`

The shared evidence model is defined in:

`app/retrieval/models.py`

### Processing Steps

1. Accept and validate the search query.
2. Return an empty list if the query contains only whitespace.
3. Search for matching entities using the Wikidata `wbsearchentities` API.
4. Retrieve entity labels, descriptions, and structured claims using `wbgetentities`.
5. Ignore deprecated claims and claims without valid values.
6. Extract readable values from supported Wikidata data types.
7. Retrieve English labels for properties and linked entities.
8. Construct readable evidence snippets from the retrieved facts.
9. Use entity descriptions as a fallback when structured evidence is unavailable.
10. Return Evidence objects containing the snippet, source, and entity reference, subject to the configured evidence limit.

### Main Classes and Methods

- `WikidataConnector`: Handles entity search and factual evidence retrieval.
- `WikidataAPIError`: Represents errors encountered while communicating with the Wikidata API.
- `search(query)`: Searches Wikidata and returns structured evidence snippets.
- `_search_entities(query)`: Searches for matching Wikidata entities.
- `_get_entities(entity_ids)`: Retrieves entity information and claims.
- `_get_labels(entity_ids)`: Retrieves English labels for properties and linked entities.
- `_extract_value(datavalue)`: Extracts readable values from Wikidata data values.
- `_request_json(params)`: Sends API requests and processes JSON responses.

### Error Handling and Validation

- Rejects non-string search queries with `TypeError`.
- Rejects non-positive timeout values.
- Validates the entity search limit to be between 1 and 50.
- Requires `max_evidence` to be at least 1.
- Handles HTTP, URL, timeout, operating-system, and JSON decoding errors through `WikidataAPIError`.
- Returns an empty list when no matching entities are found.

## 6. Integration with Other User Stories

- **US-015 - Wikidata Evidence Connector:** Retrieves factual evidence from Wikidata and converts it into the shared Evidence model.
- **US-016 - Evidence Retrieval Coordinator:** Uses the retrieval interfaces and shared Evidence model to coordinate evidence retrieval for individual claims.

The shared Evidence model allows retrieval components to exchange evidence in a consistent format.

## 7. Testing

The implementation is tested using:

`tests/test_wikidata_connector.py`

The tests cover:

- Successful structured fact retrieval.
- Correct Evidence object generation.
- Empty query handling.
- Non-string query validation.
- Handling of queries with no matching entities.
- Entity description fallback.
- Ignoring deprecated claims.
- Wikidata API error handling.
- Invalid timeout and search limit validation.

**US-015 targeted tests: 9 passed.**

The complete project test suite was also executed successfully on the US-015 branch:

**51 tests passed.**

## 8. Expected Outcome

The Wikidata connector retrieves relevant factual information and returns standardized Evidence objects containing readable snippets, source names, and Wikidata entity references.

This provides a structured evidence source for downstream claim verification and the evidence retrieval coordinator.
