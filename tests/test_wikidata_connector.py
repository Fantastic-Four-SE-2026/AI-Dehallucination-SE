
import pytest

from app.retrieval.models import Evidence
from app.retrieval.wikidata_connector import (
    WikidataAPIError,
    WikidataConnector,
)


def test_successful_structured_fact_retrieval(monkeypatch):
    connector = WikidataConnector()

    responses = [
        {
            "search": [
                {"id": "Q42", "label": "Douglas Adams"}
            ]
        },
        {
            "entities": {
                "Q42": {
                    "labels": {
                        "en": {"value": "Douglas Adams"}
                    },
                    "claims": {
                        "P19": [
                            {
                                "rank": "normal",
                                "mainsnak": {
                                    "snaktype": "value",
                                    "datavalue": {
                                        "value": {
                                            "entity-type": "item",
                                            "id": "Q350",
                                        }
                                    },
                                },
                            }
                        ]
                    },
                }
            }
        },
        {
            "entities": {
                "P19": {
                    "labels": {
                        "en": {"value": "place of birth"}
                    }
                },
                "Q350": {
                    "labels": {
                        "en": {"value": "Cambridge"}
                    }
                },
            }
        },
    ]

    def fake_request_json(params):
        return responses.pop(0)

    monkeypatch.setattr(connector, "_request_json", fake_request_json)

    results = connector.search("Douglas Adams")

    assert len(results) == 1
    assert isinstance(results[0], Evidence)
    assert results[0].snippet == (
        "Douglas Adams — place of birth — Cambridge"
    )
    assert results[0].source == "Wikidata"
    assert results[0].reference == (
        "https://www.wikidata.org/wiki/Q42"
    )


def test_empty_query_returns_empty_list():
    connector = WikidataConnector()

    assert connector.search("   ") == []


def test_non_string_query_raises_type_error():
    connector = WikidataConnector()

    with pytest.raises(TypeError):
        connector.search(123)


def test_no_matching_entities_returns_empty_list(monkeypatch):
    connector = WikidataConnector()

    monkeypatch.setattr(
        connector,
        "_request_json",
        lambda params: {"search": []},
    )

    assert connector.search("unknown subject") == []


def test_entity_without_claims_uses_description(monkeypatch):
    connector = WikidataConnector()

    responses = [
        {"search": [{"id": "Q42"}]},
        {
            "entities": {
                "Q42": {
                    "labels": {
                        "en": {"value": "Douglas Adams"}
                    },
                    "descriptions": {
                        "en": {
                            "value": "English science fiction writer"
                        }
                    },
                    "claims": {},
                }
            }
        },
    ]

    def fake_request_json(params):
        return responses.pop(0)

    monkeypatch.setattr(connector, "_request_json", fake_request_json)

    results = connector.search("Douglas Adams")

    assert len(results) == 1
    assert results[0].snippet == (
        "Douglas Adams: English science fiction writer"
    )
    assert results[0].source == "Wikidata"


def test_deprecated_claims_are_ignored(monkeypatch):
    connector = WikidataConnector()

    responses = [
        {"search": [{"id": "Q42"}]},
        {
            "entities": {
                "Q42": {
                    "labels": {
                        "en": {"value": "Douglas Adams"}
                    },
                    "claims": {
                        "P19": [
                            {
                                "rank": "deprecated",
                                "mainsnak": {
                                    "snaktype": "value",
                                    "datavalue": {
                                        "value": "Old value"
                                    },
                                },
                            }
                        ]
                    },
                }
            }
        },
    ]

    def fake_request_json(params):
        return responses.pop(0)

    monkeypatch.setattr(connector, "_request_json", fake_request_json)

    assert connector.search("Douglas Adams") == []


def test_api_failure_raises_wikidata_api_error(monkeypatch):
    connector = WikidataConnector()

    def fake_request_json(params):
        raise WikidataAPIError("Connection failed")

    monkeypatch.setattr(connector, "_request_json", fake_request_json)

    with pytest.raises(WikidataAPIError):
        connector.search("Douglas Adams")


def test_invalid_timeout_is_rejected():
    with pytest.raises(ValueError):
        WikidataConnector(timeout=0)


def test_invalid_limit_is_rejected():
    with pytest.raises(ValueError):
        WikidataConnector(limit=0)
