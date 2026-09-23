"""
DocuMind AI — Document Parser Interface
Extracts raw text from various document formats.

Phase 1 Status: INTERFACE STUB — defines the interface and returns placeholder text.
Phase 2: Implement with:
  - PyMuPDF (fitz) or pdfplumber for PDF
  - python-docx for DOCX
  - Standard library for TXT and Markdown

Integration point:
    Input:  file path or bytes + format hint
    Output: list of ExtractedPage objects (text + page number)
    Used by: ingestion pipeline → TextCleaner → TextChunker
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger("documind.ingestion.parser")


class DocumentFormat(str, Enum):
    """Supported document formats for ingestion."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MARKDOWN = "md"
    UNKNOWN = "unknown"


@dataclass
class ExtractedPage:
    """
    Text extracted from a single page or logical section of a document.
    The page_number enables accurate source citation in RAG answers.
    """
    page_number: int
    text: str
    section_heading: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ParsedDocument:
    """
    Complete result of document parsing.
    Contains all extracted pages and document-level metadata.
    """
    file_name: str
    format: DocumentFormat
    pages: list[ExtractedPage]
    total_pages: int
    raw_metadata: dict = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        """Return all page texts joined."""
        return "\n\n".join(page.text for page in self.pages if page.text.strip())


class DocumentParser:
    """
    Extracts text from institutional documents.

    Supports PDF, DOCX, TXT, and Markdown files.
    Preserves page numbers for source citation accuracy.

    Phase 1: Returns placeholder data.
    Phase 2: Implement real extraction per format.

    Example future PDF implementation:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        pages = []
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text("text")
            pages.append(ExtractedPage(page_number=page_num, text=text))
        return ParsedDocument(...)
    """

    SUPPORTED_FORMATS = {".pdf", ".docx", ".txt", ".md", ".markdown"}

    def detect_format(self, file_path: Path) -> DocumentFormat:
        """Detect document format from file extension."""
        ext = file_path.suffix.lower()
        format_map = {
            ".pdf": DocumentFormat.PDF,
            ".docx": DocumentFormat.DOCX,
            ".txt": DocumentFormat.TXT,
            ".md": DocumentFormat.MARKDOWN,
            ".markdown": DocumentFormat.MARKDOWN,
        }
        return format_map.get(ext, DocumentFormat.UNKNOWN)

    def validate(self, file_path: Path) -> None:
        """
        Validate that the file exists, is not empty, and has a supported format.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the format is unsupported or the file is empty.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if file_path.stat().st_size == 0:
            raise ValueError(f"File is empty: {file_path}")
        if file_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {file_path.suffix}. "
                f"Supported: {self.SUPPORTED_FORMATS}"
            )

    def parse(self, file_path: str | Path) -> ParsedDocument:
        """
        Parse a document and return extracted text with page metadata.

        Args:
            file_path: Path to the document file.

        Returns:
            ParsedDocument with all extracted pages.

        Raises:
            FileNotFoundError, ValueError on invalid input.
        """
        path = Path(file_path)
        self.validate(path)
        fmt = self.detect_format(path)
        logger.info("Parsing document: %s (format: %s) [STUB]", path.name, fmt)

        # TODO Phase 2: Route to format-specific parser
        # if fmt == DocumentFormat.PDF:
        #     return self._parse_pdf(path)
        # elif fmt == DocumentFormat.DOCX:
        #     return self._parse_docx(path)
        # elif fmt in (DocumentFormat.TXT, DocumentFormat.MARKDOWN):
        #     return self._parse_text(path)

        # Phase 1 stub: return placeholder
        placeholder_page = ExtractedPage(
            page_number=1,
            text=f"[Phase 1 Stub] Text extraction for {path.name} not yet implemented. "
                 f"Detected format: {fmt.value}. Connect PyMuPDF/python-docx in Phase 2.",
        )
        return ParsedDocument(
            file_name=path.name,
            format=fmt,
            pages=[placeholder_page],
            total_pages=1,
        )
