"""
Parser Tests

Tests for PDF parser, DOCX parser, and text cleaner.
Uses in-memory or temporary test fixtures so no real resume files are needed.
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.text_cleaner import clean_text, standardize_capitalization
from utils.file_handler import get_resume_files, save_processed_text, ensure_directories


# ─────────────────────────────────────────────
# TEXT CLEANER TESTS
# ─────────────────────────────────────────────

class TestTextCleaner:

    def test_removes_noise_characters(self):
        raw = "Hello\x00World\x1F Resume"
        result = clean_text(raw)
        assert "\x00" not in result
        assert "\x1F" not in result
        assert "Hello" in result

    def test_normalizes_excessive_whitespace(self):
        raw = "Python    Developer\nNew  York"
        result = clean_text(raw)
        assert "Python Developer" in result
        assert "New York" in result

    def test_collapses_multiple_blank_lines(self):
        raw = "Name\n\n\n\n\nEmail"
        result = clean_text(raw)
        # Should have at most 2 consecutive newlines
        assert "\n\n\n" not in result

    def test_normalizes_experience_heading(self):
        for variant in ["WORK EXPERIENCE", "Professional Experience", "Employment History"]:
            result = clean_text(variant)
            assert "Experience" in result

    def test_normalizes_skills_heading(self):
        for variant in ["Technical Skills", "Key Skills", "Core Competencies"]:
            result = clean_text(variant)
            assert "Skills" in result

    def test_normalizes_education_heading(self):
        for variant in ["Academic Background", "Educational Background"]:
            result = clean_text(variant)
            assert "Education" in result

    def test_normalizes_summary_heading(self):
        for variant in ["Professional Summary", "Career Summary", "About Me"]:
            result = clean_text(variant)
            assert "Summary" in result

    def test_normalizes_bullet_symbols(self):
        raw = "• Python\n● Java\n▸ AWS"
        result = clean_text(raw)
        assert "•" not in result
        assert "●" not in result
        assert "▸" not in result

    def test_empty_input_returns_empty(self):
        assert clean_text("") == ""
        assert clean_text("   ") == ""

    def test_standardize_capitalization(self):
        text = "python developer\njava engineer"
        result = standardize_capitalization(text)
        lines = result.splitlines()
        assert lines[0][0].isupper()
        assert lines[1][0].isupper()

    def test_real_resume_paragraph(self):
        sample = (
            "WORK EXPERIENCE\n"
            "Senior Backend Developer   •   TechNova\n"
            "  •  Reduced costs by 30%\n"
            "  •   Built API services\n\n\n"
            "EDUCATION\n"
            "B.Sc.   Computer Science   |   UC Berkeley   |   2016"
        )
        result = clean_text(sample)
        assert "Experience" in result
        assert "Education" in result
        assert "TechNova" in result
        assert "UC Berkeley" in result


# ─────────────────────────────────────────────
# FILE HANDLER TESTS
# ─────────────────────────────────────────────

class TestFileHandler:

    def test_get_resume_files_finds_pdf_and_docx(self, tmp_path):
        (tmp_path / "resume1.pdf").write_bytes(b"%PDF-1.4 fake data")
        (tmp_path / "resume2.docx").write_bytes(b"fake docx")
        (tmp_path / "notes.txt").write_text("ignore me")

        files = get_resume_files(str(tmp_path))
        names = [f.name for f in files]

        assert "resume1.pdf" in names
        assert "resume2.docx" in names
        assert "notes.txt" not in names

    def test_get_resume_files_raises_on_missing_dir(self):
        with pytest.raises(FileNotFoundError):
            get_resume_files("/non/existent/directory")

    def test_save_processed_text(self, tmp_path):
        source = tmp_path / "jane_doe.pdf"
        source.write_bytes(b"fake pdf")
        output_dir = str(tmp_path / "processed")

        out_path = save_processed_text("Cleaned resume text", source, output_dir)

        assert out_path.exists()
        assert out_path.name == "jane_doe.txt"
        assert out_path.read_text(encoding="utf-8") == "Cleaned resume text"

    def test_ensure_directories_creates_dirs(self, tmp_path):
        target1 = str(tmp_path / "a" / "b")
        target2 = str(tmp_path / "c")
        ensure_directories(target1, target2)
        assert Path(target1).exists()
        assert Path(target2).exists()


# ─────────────────────────────────────────────
# PDF PARSER TESTS (mocked)
# ─────────────────────────────────────────────

class TestPdfParser:

    def test_raises_on_missing_file(self):
        from parsers.pdf_parser import extract_text_from_pdf
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("/fake/path/resume.pdf")

    def test_raises_on_wrong_extension(self, tmp_path):
        from parsers.pdf_parser import extract_text_from_pdf
        f = tmp_path / "resume.txt"
        f.write_text("not a pdf")
        with pytest.raises(ValueError, match="Expected a PDF"):
            extract_text_from_pdf(str(f))

    def test_extracts_text_from_mocked_pdf(self, tmp_path):
        from parsers.pdf_parser import extract_text_from_pdf

        fake_pdf = tmp_path / "fake_resume.pdf"
        fake_pdf.write_bytes(b"%PDF-1.4 fake")

        mock_page = MagicMock()
        mock_page.extract_words.return_value = [
            {"text": "Jane", "top": 10, "x0": 5},
            {"text": "Doe", "top": 10, "x0": 50},
            {"text": "Python", "top": 30, "x0": 5},
            {"text": "Developer", "top": 30, "x0": 60},
        ]

        mock_pdf = MagicMock()
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_pdf.pages = [mock_page]

        with patch("pdfplumber.open", return_value=mock_pdf):
            result = extract_text_from_pdf(str(fake_pdf))

        assert "Jane" in result
        assert "Doe" in result
        assert "Python" in result


# ─────────────────────────────────────────────
# DOCX PARSER TESTS (mocked)
# ─────────────────────────────────────────────

class TestDocxParser:

    def test_raises_on_missing_file(self):
        from parsers.docx_parser import extract_text_from_docx
        with pytest.raises(FileNotFoundError):
            extract_text_from_docx("/fake/path/resume.docx")

    def test_raises_on_wrong_extension(self, tmp_path):
        from parsers.docx_parser import extract_text_from_docx
        f = tmp_path / "resume.txt"
        f.write_text("not a docx")
        with pytest.raises(ValueError, match="Expected a DOCX"):
            extract_text_from_docx(str(f))
