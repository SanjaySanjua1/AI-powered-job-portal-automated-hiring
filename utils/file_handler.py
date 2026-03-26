"""
File Handler Module

Handles all file system operations for the extraction pipeline:
  - Scanning input directories for resume files
  - Writing cleaned text output to the processed directory
"""

import os
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("file_handler", log_dir="logs")

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def get_resume_files(resume_dir: str) -> list[Path]:
    """
    Scan the given directory and return a list of supported resume file paths.

    Args:
        resume_dir: Path to the directory containing resume files.

    Returns:
        List of Path objects for each found resume file.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    dir_path = Path(resume_dir)
    if not dir_path.exists():
        raise FileNotFoundError(f"Resume directory not found: {resume_dir}")

    resume_files = [
        f for f in dir_path.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not resume_files:
        logger.warning(f"[FileHandler] No supported resume files found in: {resume_dir}")
    else:
        logger.info(f"[FileHandler] Found {len(resume_files)} resume file(s) in: {resume_dir}")

    return resume_files


def save_processed_text(text: str, source_file: Path, output_dir: str) -> Path:
    """
    Save cleaned resume text as a .txt file in the output directory.

    The output filename mirrors the source filename with a .txt extension.

    Args:
        text: The cleaned extracted text.
        source_file: The original Path object of the resume file.
        output_dir: Directory in which to save the output file.

    Returns:
        The Path of the saved output file.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    output_file = out_path / (source_file.stem + ".txt")
    output_file.write_text(text, encoding="utf-8")

    logger.info(f"[FileHandler] Saved processed text: {output_file}")
    return output_file


def ensure_directories(*dirs: str) -> None:
    """Create multiple directories if they do not already exist."""
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        logger.debug(f"[FileHandler] Ensured directory exists: {d}")
