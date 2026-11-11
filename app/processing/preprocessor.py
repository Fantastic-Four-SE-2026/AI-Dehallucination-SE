
from dataclasses import dataclass
import unicodedata


SYMBOL_MAP = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
}


@dataclass(frozen=True)
class PreprocessingResult:
    original_text: str
    cleaned_text: str
    position_mapping: tuple[tuple[int, int], ...]

    def map_position(self, position: int) -> int:
        """Map a cleaned character position to its original start."""
        if not 0 <= position < len(self.cleaned_text):
            raise IndexError("Cleaned-text position is out of range")

        return self.position_mapping[position][0]

    def map_span(self, start: int, end: int) -> tuple[int, int]:
        """Map a cleaned [start, end) span to its original span."""
        if not 0 <= start < end <= len(self.cleaned_text):
            raise ValueError("Invalid cleaned-text span")

        return (
            self.position_mapping[start][0],
            self.position_mapping[end - 1][1],
        )


def preprocess_text(original_text: str) -> PreprocessingResult:
    """
    Normalize whitespace, symbols and Unicode while preserving
    a mapping from cleaned characters to original text positions.
    """
    if not isinstance(original_text, str):
        raise TypeError("original_text must be a string")

    output = []
    mapping = []
    i = 0

    while i < len(original_text):
        char = original_text[i]

        # Collapse consecutive whitespace.
        if char.isspace():
            start = i

            while i < len(original_text) and original_text[i].isspace():
                i += 1

            if output and i < len(original_text):
                output.append(" ")
                mapping.append((start, i))

            continue

        # Collect a base character and its combining marks.
        start = i
        cluster = char
        i += 1

        while (
            i < len(original_text)
            and unicodedata.combining(original_text[i]) != 0
        ):
            cluster += original_text[i]
            i += 1

        # Normalize symbols and Unicode as a complete cluster.
        if len(cluster) == 1:
            cluster = SYMBOL_MAP.get(cluster, cluster)

        normalized = unicodedata.normalize("NFC", cluster)

        # Every resulting character maps to its original cluster.
        for normalized_char in normalized:
            output.append(normalized_char)
            mapping.append((start, i))

    return PreprocessingResult(
        original_text=original_text,
        cleaned_text="".join(output),
        position_mapping=tuple(mapping),
    )
