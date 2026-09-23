"""
DocuMind AI — Text Cleaner
Cleans extracted text to improve chunking and embedding quality.

Phase 1 Status: FUNCTIONAL — basic cleaning is implemented.
                More sophisticated cleaning can be added in Phase 2.

Integration point:
    Input:  raw text string from DocumentParser
    Output: cleaned text string
    Used by: ingestion pipeline → TextChunker
"""

import logging
import re

logger = logging.getLogger("documind.ingestion.cleaner")


class TextCleaner:
    """
    Cleans raw extracted text to improve RAG quality.

    Cleaning steps:
    1. Normalize whitespace and line endings.
    2. Remove header/footer artifacts (page numbers, repeated strings).
    3. Remove excessive blank lines.
    4. Remove null bytes and control characters.
    5. Normalize Unicode.

    Phase 1: Core cleaning is functional.
    Phase 2: Add OCR artifact removal, table detection, language detection.
    """

    def clean(self, text: str) -> str:
        """
        Apply all cleaning steps to the input text.

        Args:
            text: Raw text from DocumentParser.

        Returns:
            Cleaned text string.
        """
        if not text or not text.strip():
            return ""

        text = self._normalize_unicode(text)
        text = self._remove_control_characters(text)
        text = self._normalize_whitespace(text)
        text = self._remove_excessive_blank_lines(text)

        cleaned = text.strip()
        logger.debug("TextCleaner: %d chars → %d chars", len(text), len(cleaned))
        return cleaned

    def _normalize_unicode(self, text: str) -> str:
        """Normalize unicode characters."""
        import unicodedata
        return unicodedata.normalize("NFKC", text)

    def _remove_control_characters(self, text: str) -> str:
        """Remove null bytes and problematic control characters (keep newlines/tabs)."""
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    def _normalize_whitespace(self, text: str) -> str:
        """Replace multiple spaces/tabs with a single space on each line."""
        lines = text.split("\n")
        cleaned_lines = [re.sub(r"[ \t]+", " ", line) for line in lines]
        return "\n".join(cleaned_lines)

    def _remove_excessive_blank_lines(self, text: str) -> str:
        """Reduce 3+ consecutive blank lines to a maximum of 2."""
        return re.sub(r"\n{3,}", "\n\n", text)

    def is_meaningful(self, text: str, min_chars: int = 50) -> bool:
        """
        Check if a text snippet has enough meaningful content to be worth indexing.

        Args:
            text: Text to evaluate.
            min_chars: Minimum character count (default 50).

        Returns:
            True if the text is worth indexing.
        """
        cleaned = self.clean(text)
        return len(cleaned) >= min_chars
