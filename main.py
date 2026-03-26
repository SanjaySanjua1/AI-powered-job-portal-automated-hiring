"""
Main Pipeline: Resume Text Extraction Engine

Orchestrates the full Extract -> Clean -> Save pipeline.

Usage:
    # Activate venv first!
    python main.py

    # Optional: specify custom directories
    python main.py --resume-dir data/resumes --output-dir data/processed

Resumes placed in data/resumes/ (PDF or DOCX) will be:
  1. Extracted using the appropriate parser
  2. Cleaned using the text cleaner
  3. Saved as .txt files in data/processed/
  4. Logged in logs/extraction.log
"""

import argparse
import sys
import traceback
from pathlib import Path

from parsers.pdf_parser import extract_text_from_pdf
from parsers.docx_parser import extract_text_from_docx
from utils.text_cleaner import clean_text, standardize_capitalization
from utils.file_handler import get_resume_files, save_processed_text, ensure_directories
from utils.logger import setup_logger

logger = setup_logger("main_pipeline", log_dir="logs")

DEFAULT_RESUME_DIR = "data/resumes"
DEFAULT_OUTPUT_DIR = "data/processed"


def extract_text(file_path: Path) -> str:
    """Dispatch to the correct parser based on file extension."""
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(str(file_path))
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(str(file_path))
    else:
        raise ValueError(f"Unsupported file type for extraction: {ext}")


def process_resume(file_path: Path, output_dir: str) -> dict:
    """
    Run the full pipeline for a single resume file.

    Returns a result dict with keys: file, status, output_path, error.
    """
    result = {"file": file_path.name, "status": "success", "output_path": None, "error": None}

    try:
        logger.info(f"Processing: {file_path.name}")

        # Step 1: Extract
        raw_text = extract_text(file_path)

        # Step 2: Clean
        cleaned = clean_text(raw_text)
        cleaned = standardize_capitalization(cleaned)

        if not cleaned.strip():
            logger.warning(f"[Pipeline] No readable text extracted from: {file_path.name}")
            result["status"] = "empty"
            return result

        # Step 3: Save
        output_path = save_processed_text(cleaned, file_path, output_dir)
        result["output_path"] = str(output_path)
        logger.info(f"[Pipeline] Successfully processed: {file_path.name} -> {output_path.name}")

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        logger.error(f"[Pipeline] Failed to process {file_path.name}: {e}")
        logger.debug(traceback.format_exc())

    return result


def run_pipeline(resume_dir: str, output_dir: str) -> None:
    """Run the full extraction pipeline over all resumes in resume_dir."""
    logger.info("=" * 60)
    logger.info("ZecPath Resume Extraction Pipeline - STARTING")
    logger.info(f"Resume Directory : {resume_dir}")
    logger.info(f"Output Directory : {output_dir}")
    logger.info("=" * 60)

    # Ensure directories exist
    ensure_directories(resume_dir, output_dir, "logs")

    # Discover files
    try:
        resume_files = get_resume_files(resume_dir)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    if not resume_files:
        logger.info("[Pipeline] No resumes to process. Place PDF/DOCX files in data/resumes/ and rerun.")
        return

    # Process each file
    results = [process_resume(f, output_dir) for f in resume_files]

    # Summary report
    success = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    empty = [r for r in results if r["status"] == "empty"]

    logger.info("=" * 60)
    logger.info("ZecPath Resume Extraction Pipeline - COMPLETE")
    logger.info(f"  Total   : {len(results)}")
    logger.info(f"  Success : {len(success)}")
    logger.info(f"  Empty   : {len(empty)}")
    logger.info(f"  Failed  : {len(failed)}")
    if failed:
        for r in failed:
            logger.error(f"  FAILED  : {r['file']} | {r['error']}")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="ZecPath Resume Text Extraction Engine"
    )
    parser.add_argument(
        "--resume-dir",
        default=DEFAULT_RESUME_DIR,
        help=f"Directory containing raw resume files (default: {DEFAULT_RESUME_DIR})"
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to write cleaned text files (default: {DEFAULT_OUTPUT_DIR})"
    )
    args = parser.parse_args()
    run_pipeline(args.resume_dir, args.output_dir)


if __name__ == "__main__":
    main()
