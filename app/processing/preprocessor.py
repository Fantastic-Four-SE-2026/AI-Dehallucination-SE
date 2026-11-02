
from dataclasses import dataclass


@dataclass(frozen=True)
class PreprocessingResult:
    """Store original text, cleaned text, and position mapping."""

    original_text: str
    cleaned_text: str
    position_map: tuple[int, ...]

    def map_span_to_original(self, start: int, end: int) -> tuple[int, int]:
        """Map a cleaned-text [start, end) span to original offsets."""
        if not 0 <= start <= end <= len(self.cleaned_text):
            raise ValueError("Invalid cleaned-text span")

        if start == end:
            if start == len(self.cleaned_text):
                return len(self.original_text), len(self.original_text)
            pos = self.position_map[start]
            return pos, pos

        return self.position_map[start], self.position_map[end - 1] + 1


def preprocess_text(text: str) -> PreprocessingResult:
    """Collapse repeated whitespace while preserving character positions."""
    cleaned_chars = []
    position_map = []

    for index, char in enumerate(text):
        if char.isspace():
            if cleaned_chars and cleaned_chars[-1] != " ":
                cleaned_chars.append(" ")
                position_map.append(index)
        else:
            cleaned_chars.append(char)
            position_map.append(index)

    # Remove leading whitespace.
    if cleaned_chars and cleaned_chars[0] == " ":
        cleaned_chars.pop(0)
        position_map.pop(0)

    # Remove trailing whitespace.
    if cleaned_chars and cleaned_chars[-1] == " ":
        cleaned_chars.pop()
        position_map.pop()

    return PreprocessingResult(
        original_text=text,
        cleaned_text="".join(cleaned_chars),
        position_map=tuple(position_map),
    )
