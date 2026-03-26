"""
Text Cleaner Module

Cleans and normalizes raw resume text extracted from PDF/DOCX files.
Removes noise, collapses whitespace, and standardizes common resume section headings
to align with the defined Resume JSON schema entity structure.
"""

import re
from utils.logger import setup_logger

logger = setup_logger("text_cleaner", log_dir="logs")

# Map of common heading variants to canonical names (aligned with JSON schema fields)
HEADING_NORMALIZATION_MAP = {
    r"\b(work\s+experience|professional\s+experience|employment\s+history|career\s+history)\b": "Experience",
    r"\b(technical\s+skills|key\s+skills|core\s+competencies|skills\s+&\s+expertise|skills\s+and\s+expertise)\b": "Skills",
    r"\b(education|academic\s+background|academic\s+qualifications|educational\s+background)\b": "Education",
    r"\b(certifications\s+&\s+awards|certifications\s+and\s+awards|licenses\s+&\s+certifications)\b": "Certifications",
    r"\b(personal\s+summary|professional\s+summary|career\s+summary|profile\s+summary|about\s+me)\b": "Summary",
    r"\b(contact\s+information|contact\s+details|personal\s+information|personal\s+details)\b": "Personal Information",
    r"\b(projects\s+&\s+achievements|key\s+achievements|notable\s+projects)\b": "Projects",
}

# Characters that are non-printable or noise in extracted text
NOISE_PATTERN = re.compile(
    r"[^\x20-\x7Eàáâãäåèéêëìíîïòóôõöùúûüýÿ\n\r\t]"
)

# Excessive horizontal whitespace (not newlines)
MULTI_SPACE_PATTERN = re.compile(r"[ \t]{2,}")

# More than two consecutive newlines
MULTI_NEWLINE_PATTERN = re.compile(r"\n{3,}")

# Bullet-like Unicode artifacts
BULLET_PATTERN = re.compile(r"^[\•\●\◦\▪\▸\-\*]\s*", re.MULTILINE)


def clean_text(raw_text: str) -> str:
    """
    Full cleaning pipeline for raw resume text.

    Steps:
      1. Remove non-printable/noise characters
      2. Normalize bullet point symbols
      3. Normalize heading variants to schema-aligned names
      4. Collapse excessive whitespace (spaces and newlines)
      5. Strip leading/trailing whitespace per line

    Args:
        raw_text: The raw extracted text from a parser.

    Returns:
        Cleaned and normalized text string.
    """
    if not raw_text or not raw_text.strip():
        logger.warning("[Cleaner] Received empty text, returning empty string.")
        return ""

    text = raw_text

    # Step 1: Remove noise characters
    text = NOISE_PATTERN.sub("", text)

    # Step 2: Normalize bullet symbols to a standard hyphen
    text = BULLET_PATTERN.sub("- ", text)

    # Step 3: Normalize section headings (case-insensitive)
    for pattern, replacement in HEADING_NORMALIZATION_MAP.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Step 4: Collapse multiple horizontal spaces
    text = MULTI_SPACE_PATTERN.sub(" ", text)

    # Step 5: Strip each line
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)

    # Step 6: Collapse excessive blank lines
    text = MULTI_NEWLINE_PATTERN.sub("\n\n", text)

    # Step 7: Final strip
    text = text.strip()

    logger.debug(f"[Cleaner] Cleaned text to {len(text)} characters.")
    return text


def standardize_capitalization(text: str) -> str:
    """
    Ensure each sentence/line starts with a capital letter where appropriate.
    Applied after clean_text().
    """
    lines = text.splitlines()
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped[0].isupper():
            stripped = stripped[0].upper() + stripped[1:]
        result.append(stripped)
    return "\n".join(result)
