
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.retrieval.models import Evidence


class WikidataAPIError(RuntimeError):
    """Raised when the Wikidata API cannot provide a valid response."""



class WikidataConnector:
    """Retrieves structured factual evidence from Wikidata."""

    API_URL = "https://www.wikidata.org/w/api.php"
    SOURCE_NAME = "Wikidata"

    def __init__(
        self,
        timeout: float = 5.0,
        limit: int = 5,
        max_evidence: int = 20,
        user_agent: str = "AI-Dehallucination-Project/1.0",
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero.")

        if max_evidence < 1:
            raise ValueError("max_evidence must be at least 1.")

        self.max_evidence = max_evidence

        if limit < 1 or limit > 50:
            raise ValueError("limit must be between 1 and 50.")

        self.timeout = timeout
        self.limit = limit
        self.user_agent = user_agent

   
    def _request_json(self, params: dict) -> dict:
        """Send a request to Wikidata and return its JSON response."""

        url = f"{self.API_URL}?{urlencode(params)}"
        request = Request(
            url,
            headers={"User-Agent": self.user_agent},
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))

        except (
            HTTPError,
            URLError,
            TimeoutError,
            OSError,
            json.JSONDecodeError,
        ) as exc:
            raise WikidataAPIError(
                f"Wikidata API request failed: {exc}"
            ) from exc

    def _search_entities(self, query: str) -> list[dict]:
        """Find Wikidata entities matching the supplied query."""

        data = self._request_json({
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "uselang": "en",
            "format": "json",
            "limit": self.limit,
        })

        return data.get("search", [])

    def _get_entities(self, entity_ids: list[str]) -> dict:
        """Retrieve labels and structured claims for entity IDs."""

        if not entity_ids:
            return {}

        data = self._request_json({
            "action": "wbgetentities",
            "ids": "|".join(entity_ids),
            "props": "labels|descriptions|claims",
            "languages": "en",
            "format": "json",
        })

        return data.get("entities", {})

    @staticmethod
    def _extract_value(datavalue: dict) -> tuple[str | None, str | None]:
        """Extract a readable value and optional linked entity ID."""

        value = datavalue.get("value")

        if isinstance(value, dict):
            if value.get("entity-type"):
                entity_id = value.get("id")
                return entity_id, entity_id

            if "amount" in value:
                return str(value["amount"]), None

            if "time" in value:
                return str(value["time"]), None

            if "text" in value:
                return str(value["text"]), None

            if "latitude" in value and "longitude" in value:
                return (
                    f'{value["latitude"]}, {value["longitude"]}',
                    None,
                )

            return None, None

        if isinstance(value, (str, int, float)):
            return str(value), None

        return None, None

    def _get_labels(self, entity_ids: list[str]) -> dict[str, str]:
        """Retrieve English labels for property and linked entity IDs."""

        if not entity_ids:
            return {}

        data = self._request_json({
            "action": "wbgetentities",
            "ids": "|".join(entity_ids[:50]),
            "props": "labels",
            "languages": "en",
            "format": "json",
        })

        labels = {}

        for entity_id, entity in data.get("entities", {}).items():
            label = entity.get("labels", {}).get("en", {}).get("value")

            if label:
                labels[entity_id] = label

        return labels

    def search(self, query: str) -> list[Evidence]:
        """Search Wikidata and return structured evidence snippets."""

        if not isinstance(query, str):
            raise TypeError("query must be a string.")

        query = query.strip()

        if not query:
            return []

        search_results = self._search_entities(query)

        if not search_results:
            return []

        entity_ids = [
            item["id"]
            for item in search_results
            if item.get("id")
        ]

        entities = self._get_entities(entity_ids)

        facts = []
        label_ids = []

        for entity_id in entity_ids:
            entity = entities.get(entity_id, {})
            entity_label = (
                entity.get("labels", {})
                .get("en", {})
                .get("value", entity_id)
            )

            for property_id, statements in entity.get("claims", {}).items():
                for statement in statements:
                    if statement.get("rank") == "deprecated":
                        continue

                    snak = statement.get("mainsnak", {})

                    if snak.get("snaktype") != "value":
                        continue

                    datavalue = snak.get("datavalue", {})
                    value, linked_id = self._extract_value(datavalue)

                    if value is None:
                        continue

                    label_ids.append(property_id)

                    if linked_id:
                        label_ids.append(linked_id)

                    facts.append((
                        entity_id,
                        entity_label,
                        property_id,
                        value,
                        linked_id,
                    ))

        labels = self._get_labels(list(dict.fromkeys(label_ids)))

        evidence = []

        for (
            entity_id,
            entity_label,
            property_id,
            value,
            linked_id,
        ) in facts:
            property_label = labels.get(property_id, property_id)

            if linked_id:
                value = labels.get(linked_id, value)

            snippet = (
                f"{entity_label} — {property_label} — {value}"
            )

            evidence.append(Evidence(
                snippet=snippet,
                source=self.SOURCE_NAME,
                reference=f"https://www.wikidata.org/wiki/{entity_id}",
            ))

        # Use the entity description when no structured facts are available.
        if not evidence:
            for entity_id in entity_ids:
                entity = entities.get(entity_id, {})
                description = (
                    entity.get("descriptions", {})
                    .get("en", {})
                    .get("value")
                )

                if description:
                    label = (
                        entity.get("labels", {})
                        .get("en", {})
                        .get("value", entity_id)
                    )

                    evidence.append(Evidence(
                        snippet=f"{label}: {description}",
                        source=self.SOURCE_NAME,
                        reference=(
                            f"https://www.wikidata.org/wiki/{entity_id}"
                        ),
                    ))

        return evidence[:self.max_evidence]
