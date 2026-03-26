"""
DOCX Parser Module

Extracts raw text from DOCX resume files using python-docx.
Handles paragraphs and table cells to cover all common resume layouts.
"""

from pathlib import Path
from docx import Document
from docx.oxml.ns import qn
from utils.logger import setup_logger

logger = setup_logger("docx_parser", log_dir="logs")


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract all text from a DOCX file.

    Iterates through document body elements in order, extracting both
    paragraph text and table cell text to cover all resume layouts.

    Args:
        file_path: Absolute or relative path to the DOCX file.

    Returns:
        Raw extracted text as a single string.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid DOCX file.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"DOCX file not found: {file_path}")
    if path.suffix.lower() not in (".docx", ".doc"):
        raise ValueError(f"Expected a DOCX file, got: {path.suffix}")

    logger.info(f"[DOCX] Starting extraction: {path.name}")
    text_parts: list[str] = []

    try:
        doc = Document(str(path))

        # Iterate body-level XML elements to preserve original reading order
        for element in doc.element.body:
            tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

            if tag == "p":
                # Standard paragraph element
                paragraph_text = element.text_content() if hasattr(element, "text_content") else _get_para_text(element)
                if paragraph_text.strip():
                    text_parts.append(paragraph_text.strip())

            elif tag == "tbl":
                # Table element - iterate all cells
                table_text = _extract_table_text(element)
                if table_text.strip():
                    text_parts.append(table_text)

    except Exception as e:
        logger.error(f"[DOCX] Failed to extract from {path.name}: {e}")
        raise

    combined = "\n".join(text_parts)
    logger.info(f"[DOCX] Completed extraction: {path.name} ({len(combined)} characters)")
    return combined


def _get_para_text(para_element) -> str:
    """Extract text from a paragraph XML element."""
    texts = []
    for r in para_element.iter(qn("w:t")):
        if r.text:
            texts.append(r.text)
    return "".join(texts)


def _extract_table_text(tbl_element) -> str:
    """Extract text from a table XML element, reading left-to-right, top-to-bottom."""
    rows_text: list[str] = []
    for row in tbl_element.iter(qn("w:tr")):
        cells_text: list[str] = []
        for cell in row.iter(qn("w:tc")):
            cell_content = []
            for para in cell.iter(qn("w:p")):
                para_text = _get_para_text(para)
                if para_text.strip():
                    cell_content.append(para_text.strip())
            cells_text.append(" ".join(cell_content))
        row_line = " | ".join(filter(None, cells_text))
        if row_line.strip():
            rows_text.append(row_line)
    return "\n".join(rows_text)
