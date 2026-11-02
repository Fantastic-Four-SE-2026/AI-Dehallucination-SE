
import unittest

from app.processing.preprocessor import preprocess_text


class PreprocessorTests(unittest.TestCase):

    def test_collapses_whitespace(self):
        result = preprocess_text("  Hello   world\n\tagain!  ")
        self.assertEqual(result.cleaned_text, "Hello world again!")

    def test_preserves_original_text(self):
        original = "Hello   world\n"
        result = preprocess_text(original)
        self.assertEqual(result.original_text, original)

    def test_maps_word_to_original_position(self):
        original = "  The   sky is blue.  "
        result = preprocess_text(original)

        start = result.cleaned_text.index("sky")
        end = start + len("sky")
        original_start, original_end = result.map_span_to_original(
            start, end
        )

        self.assertEqual(original[original_start:original_end], "sky")

    def test_empty_text(self):
        result = preprocess_text(" \t\n ")
        self.assertEqual(result.cleaned_text, "")
        self.assertEqual(result.position_map, ())

    def test_invalid_span_raises_error(self):
        result = preprocess_text("hello")
        with self.assertRaises(ValueError):
            result.map_span_to_original(0, 99)

    def test_position_map_matches_cleaned_text_length(self):
        result = preprocess_text("A   simple\nexample.")
        self.assertEqual(
            len(result.position_map),
            len(result.cleaned_text),
        )


if __name__ == "__main__":
    unittest.main()
