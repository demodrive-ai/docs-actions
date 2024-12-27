"""Unit tests for the llms_txt_action.utils module."""
# ruff: noqa: S101

from unittest.mock import Mock, patch

import pytest
from docling.datamodel.base_models import ConversionStatus

from llms_txt_action.utils import (
    concatenate_markdown_files,
    convert_html_to_markdown,
    generate_docs_structure,
    html_to_markdown,
)


# Fixtures
@pytest.fixture
def sample_html_content():
    """Sample HTML content for testing."""
    return """
    <html>
        <body>
            <div>Some pre-content</div>
            <h1>First Heading</h1>
            <p>Test content</p>
        </body>
    </html>
    """


@pytest.fixture
def sample_html_file(tmp_path, sample_html_content):
    """Sample HTML file for testing."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html_content)
    return html_file


@pytest.fixture
def sample_sitemap_content():
    """Sample sitemap.xml content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/docling/</loc>
        </url>
        <url>
            <loc>https://example.com/docling/page1</loc>
        </url>
    </urlset>
    """


@pytest.fixture
def sample_sitemap_file(tmp_path, sample_sitemap_content):
    """Sample sitemap.xml file for testing."""
    sitemap_file = tmp_path / "sitemap.xml"
    sitemap_file.write_text(sample_sitemap_content)
    return sitemap_file


# Tests for html_to_markdown
def test_html_to_markdown_success(sample_html_file):
    """Test HTML to markdown conversion."""
    with patch("docling.document_converter.DocumentConverter") as mock_converter_cls:
        mock_converter = Mock()
        mock_result = Mock()
        mock_result.status = ConversionStatus.SUCCESS
        markdown_content = "# First Heading\n\nTest content"
        mock_result.document.export_to_markdown.return_value = markdown_content
        mock_converter.convert.return_value = mock_result
        mock_converter_cls.return_value = mock_converter

        result = html_to_markdown(sample_html_file)
        assert result == markdown_content


# Tests for convert_html_to_markdown
def test_convert_html_to_markdown_success(tmp_path, sample_html_file):
    """Test HTML to markdown conversion success."""
    with patch("llms_txt_action.utils.html_to_markdown") as mock_converter:
        mock_converter.return_value = "# Converted content"

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        sample_html_file.rename(input_dir / "test.html")

        result = convert_html_to_markdown(str(input_dir))
        assert len(result) == 1
        assert result[0].suffix == ".md"


def test_convert_html_to_markdown_invalid_path():
    """Test convert html to markdown invalid path."""
    with pytest.raises(
        ValueError,
        match="The input path nonexistent_path is not a directory.",
    ):
        convert_html_to_markdown("nonexistent_path")


# Tests for generate_docs_structure
def test_generate_docs_structure(sample_sitemap_file):
    """Test generate docs structure."""
    result = generate_docs_structure(str(sample_sitemap_file))
    assert "# Docling Documentation" in result
    assert "Page1" in result
    assert "This is a placeholder summary" in result


# Tests for concatenate_markdown_files
def test_concatenate_markdown_files(tmp_path):
    """Test concatenate markdown files."""
    # Create sample markdown files
    file1 = tmp_path / "file1.md"
    file2 = tmp_path / "file2.md"
    file1.write_text("Content 1")
    file2.write_text("Content 2")

    output_file = tmp_path / "output.md"
    concatenate_markdown_files([file1, file2], output_file)

    result = output_file.read_text()
    assert "Content 1" in result
    assert "Content 2" in result
