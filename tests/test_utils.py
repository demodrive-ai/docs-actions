"""Unit tests for the llms_txt_action.utils module."""
# ruff: noqa: S101

from unittest.mock import Mock, patch

import pytest
from docling.datamodel.base_models import ConversionStatus

from llms_txt_action.utils import (
    concatenate_markdown_files,
    convert_html_to_markdown,
    extract_heading,
    generate_docs_structure,
    html_to_markdown,
    summarize_page,
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
            <loc>https://example.com/</loc>
        </url>
        <url>
            <loc>https://example.com/configuration/azure.html</loc>
        </url>
        <url>
            <loc>https://example.com/configuration/aws/</loc>
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


def test_convert_html_to_markdown_handles_conversion_failure(
    tmp_path,
    sample_html_file,
):
    """Test handling of conversion failures."""
    with patch("llms_txt_action.utils.html_to_markdown") as mock_converter:
        mock_converter.side_effect = Exception("Conversion failed")

        input_dir = tmp_path / "input"
        input_dir.mkdir()
        sample_html_file.rename(input_dir / "test.html")

        result = convert_html_to_markdown(str(input_dir))
        assert len(result) == 0


# Tests for summarize_page
def test_summarize_page_with_model():
    """Test summarize page with model API key."""
    with (
        patch("llms_txt_action.utils.completion") as mock_completion,
        patch.dict("os.environ", {"MODEL_API_KEY": "."}),
    ):
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test summary"))]
        mock_completion.return_value = mock_response

        result = summarize_page("Test content", "gpt-3.5-turbo")
        assert result == "Test summary"


def test_summarize_page_without_model():
    """Test summarize page without model API key."""
    with (
        patch.dict("os.environ", clear=True),
        patch("llms_txt_action.utils.extract_heading") as mock_extract,
    ):
        mock_extract.return_value = "Test Heading"
        result = summarize_page("# Test Heading\nContent", "gpt-3.5-turbo")
        assert result == "Test Heading"


# Tests for extract_heading
def test_extract_heading_with_h1():
    """Test extract heading with h1."""
    content = "# Main Heading\nContent"
    assert extract_heading(content) == "Main Heading"


def test_extract_heading_with_h2():
    """Test extract heading with h2."""
    content = "## Secondary Heading\nContent"
    assert extract_heading(content) == "Secondary Heading"


def test_extract_heading_no_heading():
    """Test extract heading with no heading."""
    content = "Just content"
    assert extract_heading(content) == ""


# Tests for generate_docs_structure
def test_generate_docs_structure(tmp_path, sample_sitemap_file):
    """Test generate docs structure."""
    # Create test markdown files
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    index_md = docs_dir / "index.md"
    index_md.write_text("# Welcome to MkDocs")

    config_dir = docs_dir / "configuration"
    config_dir.mkdir()

    azure_md = config_dir / "azure.md"
    azure_md.write_text("# Azure Configuration")

    aws_dir = config_dir / "aws"
    aws_dir.mkdir()
    aws_md = aws_dir / "index.md"
    aws_md.write_text("# AWS Configurations")

    # Copy sample sitemap file to docs directory
    sitemap_path = docs_dir / "sitemap.xml"
    sitemap_path.write_text(sample_sitemap_file.read_text())

    result = generate_docs_structure(
        str(docs_dir),
        "sitemap.xml",
        "gpt-3.5-turbo",
    )

    assert "# Docs" in result
    assert "Welcome to MkDocs" in result
    assert "Azure Configuration" in result
    assert "AWS Configurations" in result


def test_generate_docs_structure_missing_sitemap(tmp_path):
    """Test generate docs structure with missing sitemap."""
    with pytest.raises(FileNotFoundError):
        generate_docs_structure(str(tmp_path), "nonexistent.xml", "gpt-3.5-turbo")


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
    assert result.count("\n\n") >= 1  # Check for separator between files


def test_concatenate_markdown_files_empty_list(tmp_path):
    """Test concatenate markdown files with empty list."""
    output_file = tmp_path / "output.md"
    concatenate_markdown_files([], output_file)
    assert output_file.exists()
    assert output_file.read_text() == ""
