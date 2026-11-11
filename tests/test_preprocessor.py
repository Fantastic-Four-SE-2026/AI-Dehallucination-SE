
from app.processing.preprocessor import preprocess_text


def test_whitespace_is_normalized():
    result = preprocess_text("Hello    world\n\tagain")

    assert result.cleaned_text == "Hello world again"


def test_symbols_are_normalized():
    result = preprocess_text("It’s “reliable”—yes…")

    assert result.cleaned_text == 'It\'s "reliable"-yes...'


def test_position_maps_to_original_text():
    original = "Hello    world"
    result = preprocess_text(original)

    # "world" starts at position 9 in the original text.
    cleaned_position = result.cleaned_text.index("world")

    assert result.map_position(cleaned_position) == 9


def test_span_maps_to_original_text():
    original = "Hello    world"
    result = preprocess_text(original)

    start = result.cleaned_text.index("world")
    end = start + len("world")

    original_start, original_end = result.map_span(start, end)

    assert original[original_start:original_end] == "world"


def test_original_text_is_unchanged():
    original = "  Hello    world!  "
    result = preprocess_text(original)

    assert result.original_text == original
    assert original == "  Hello    world!  "


def test_empty_text():
    result = preprocess_text("")

    assert result.cleaned_text == ""
    assert result.position_mapping == ()


def test_mapping_covers_every_cleaned_character():
    result = preprocess_text("A   B’s")

    assert len(result.position_mapping) == len(result.cleaned_text)


def test_leading_and_trailing_whitespace():
    result = preprocess_text("   Hello World   ")

    assert result.cleaned_text == "Hello World"
    assert result.map_position(0) == 3


def test_multiple_newlines_and_tabs():
    result = preprocess_text("Hello\n\n\t\tWorld")

    assert result.cleaned_text == "Hello World"

    world_position = result.cleaned_text.index("World")
    assert result.map_position(world_position) == 9


def test_ellipsis_position_mapping():
    original = "Wait…"
    result = preprocess_text(original)

    assert result.cleaned_text == "Wait..."

    for position in range(4, 7):
        assert result.map_position(position) == 4


def test_invalid_position():
    result = preprocess_text("Hello")

    import pytest

    with pytest.raises(IndexError):
        result.map_position(5)


def test_invalid_span():
    result = preprocess_text("Hello")

    import pytest

    with pytest.raises(ValueError):
        result.map_span(3, 2)


def test_unicode_text_preserved():
    original = "Café नमस्ते 世界"
    result = preprocess_text(original)

    # Unicode text should remain unchanged.
    assert result.cleaned_text == original

    # Every cleaned character must have a valid original range.
    for position in range(len(result.cleaned_text)):
        start, end = result.position_mapping[position]

        assert 0 <= start < end <= len(original)

    # The complete cleaned span must map to the complete original text.
    start, end = result.map_span(0, len(result.cleaned_text))

    assert original[start:end] == original



import pytest


def test_decomposed_unicode_normalization():
    original = "Cafe\u0301"
    result = preprocess_text(original)

    assert result.cleaned_text == "Café"

    # The normalized é represents the original e + combining accent.
    start, end = result.position_mapping[-1]
    assert original[start:end] == "e\u0301"


def test_ellipsis_span_mapping():
    original = "Wait…"
    result = preprocess_text(original)

    start, end = result.map_span(4, 7)

    assert original[start:end] == "…"


def test_collapsed_whitespace_span_mapping():
    original = "Hello    world"
    result = preprocess_text(original)

    start, end = result.map_span(5, 6)

    assert original[start:end] == "    "


def test_non_string_input():
    with pytest.raises(TypeError):
        preprocess_text(123)


def test_mapping_boundaries():
    original = "  Hello   world…  "
    result = preprocess_text(original)

    for start, end in result.position_mapping:
        assert 0 <= start < end <= len(original)

