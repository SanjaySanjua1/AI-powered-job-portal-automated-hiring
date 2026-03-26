"""
PDF Parser Module

Extracts raw text from single and multi-page PDF resume files using pdfplumber.
Handles column layouts by ordering text blocks by vertical position.
"""

import pdfplumber
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("pdf_parser", log_dir="logs")


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file, handling multi-page documents.

    Args:
        file_path: Absolute or relative path to the PDF file.

    Returns:
        Raw extracted text as a single string.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid PDF.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {path.suffix}")

    logger.info(f"[PDF] Starting extraction: {path.name}")
    full_text_parts = []

    try:
        with pdfplumber.open(str(path)) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"[PDF] {path.name} has {total_pages} page(s).")

            for i, page in enumerate(pdf.pages, start=1):
                page_text = _extract_page_text(page, page_num=i, filename=path.name)
                if page_text:
                    full_text_parts.append(page_text)

    except Exception as e:
        logger.error(f"[PDF] Failed to extract from {path.name}: {e}")
        raise

    combined = "\n".join(full_text_parts)
    logger.info(f"[PDF] Completed extraction: {path.name} ({len(combined)} characters)")
    return combined


def _extract_page_text(page, page_num: int, filename: str) -> str:
    """
    Extract text from a single pdfplumber Page object.

    Attempts word-level extraction ordered by vertical position (top)
    to handle column-based layouts. Falls back to simple page.extract_text().
    """
    try:
        words = page.extract_words(
            x_tolerance=3,
            y_tolerance=3,
            keep_blank_chars=False,
            use_text_flow=True,
        )
        if words:
            # Sort by vertical position then horizontal for column handling
            words_sorted = sorted(words, key=lambda w: (round(w["top"] / 5) * 5, w["x0"]))
            lines: list[str] = []
            current_line_top = None
            current_line_words = []

            for word in words_sorted:
                word_top = round(word["top"] / 5) * 5
                if current_line_top is None or abs(word_top - current_line_top) <= 5:
                    current_line_words.append(word["text"])
                    current_line_top = word_top
                else:
                    lines.append(" ".join(current_line_words))
                    current_line_words = [word["text"]]
                    current_line_top = word_top

            if current_line_words:
                lines.append(" ".join(current_line_words))

            return "\n".join(lines)
        else:
            # Fallback: standard extraction
            text = page.extract_text()
            return text or ""

    except Exception as e:
        logger.warning(f"[PDF] Page {page_num} of {filename} failed word extraction, using fallback: {e}")
        try:
            return page.extract_text() or ""
        except Exception:
            return ""
