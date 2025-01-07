"""Unit tests for the llms_txt_action.utils module."""
# ruff: noqa: S101, S314, E501

import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch

import pytest
from docling.datamodel.base_models import ConversionStatus

from llms_txt_action.utils import (
    _convert_url_to_file_path,
    _extract_heading,
    _extract_site_url,
    concatenate_markdown_files,
    generate_docs_structure,
    generate_summary,
    html_folder_to_markdown,
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

        result = html_folder_to_markdown(str(input_dir))
        assert len(result) == 1
        assert result[0].suffix == ".md"


def test_convert_html_to_markdown_invalid_path():
    """Test convert html to markdown invalid path."""
    with pytest.raises(
        ValueError,
        match="The input path nonexistent_path is not a directory.",
    ):
        html_folder_to_markdown("nonexistent_path")


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

        result = html_folder_to_markdown(str(input_dir))
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

        result = generate_summary("Test content", "gpt-3.5-turbo")
        assert result == "Test summary"


def test_summarize_page_without_model():
    """Test summarize page without model API key."""
    with (
        patch.dict("os.environ", clear=True),
        patch("llms_txt_action.utils._extract_heading") as mock_extract,
    ):
        mock_extract.return_value = "Test Heading"
        result = generate_summary("# Test Heading\nContent", "gpt-3.5-turbo")
        assert result == "Test Heading"


# Tests for extract_heading
def test_extract_heading_with_h1():
    """Test extract heading with h1."""
    content = "# Main Heading\nContent"
    assert _extract_heading(content) == "Main Heading"


def test_extract_heading_with_h2():
    """Test extract heading with h2."""
    content = "## Secondary Heading\nContent"
    assert _extract_heading(content) == "Secondary Heading"


def test_extract_heading_no_heading():
    """Test extract heading with no heading."""
    content = "Just content"
    assert _extract_heading(content) == ""


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


def test_extract_site_url_common_prefix():
    """Test extracting site URL with common prefix."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://example.com/page1</loc></url>
        <url><loc>https://example.com/page2</loc></url>
        <url><loc>https://example.com/subdir/page3</loc></url>
    </urlset>
    """
    root = ET.fromstring(xml_content)
    assert _extract_site_url(root) == "https://example.com/"


def test_extract_site_url_common_prefix_with_subdir():
    """Test extracting site URL with common prefix."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://example.com/page1/</loc></url>
        <url><loc>https://example.com/page1/subdir/</loc></url>
        <url><loc>https://example.com/page1/subdir2/</loc></url>
    </urlset>
    """
    root = ET.fromstring(xml_content)
    assert _extract_site_url(root) == "https://example.com/page1/"


def test_extract_site_url_empty_sitemap():
    """Test extracting site URL from empty sitemap."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    </urlset>
    """
    root = ET.fromstring(xml_content)
    with pytest.raises(ValueError, match="No URLs found in sitemap"):
        _extract_site_url(root)


def test_extract_site_url_single_url():
    """Test extracting site URL with single URL."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://example.com/</loc></url>
    </urlset>
    """
    root = ET.fromstring(xml_content)
    assert _extract_site_url(root) == "https://example.com/"


@pytest.fixture
def setup_mock_files(tmp_path):
    """Create mock files for testing."""
    # Create regular markdown files
    (tmp_path / "index.md").touch()
    (tmp_path / "docs.md").touch()

    # Create nested structure
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    (nested_dir / "index.md").touch()

    # Create structure with latest directory
    latest_dir = tmp_path / "latest"
    latest_dir.mkdir()
    (latest_dir / "guide.md").touch()
    (tmp_path / "guide.md").touch()  # Same file without latest/

    # Create structure with locale
    en_dir = tmp_path / "en"
    en_dir.mkdir()
    (en_dir / "about.md").touch()
    (tmp_path / "about.md").touch()  # Same file without locale

    (tmp_path / "non_locale.md").touch()
    (nested_dir / "non_locale.md").touch()

    return tmp_path


def test_basic_conversion(setup_mock_files, monkeypatch):
    """Test basic URL to file path conversion."""
    monkeypatch.chdir(setup_mock_files)

    site_url = "https://example.com/"

    # Test index page
    assert (
        _convert_url_to_file_path("https://example.com/", site_url, setup_mock_files)
        == "index.md"
    )
    assert (
        _convert_url_to_file_path(
            "https://example.com/index.html",
            site_url,
            setup_mock_files,
        )
        == "index.md"
    )

    # Test HTML extension
    assert (
        _convert_url_to_file_path(
            "https://example.com/docs.html",
            site_url,
            setup_mock_files,
        )
        == "docs.md"
    )


def test_nested_paths(setup_mock_files, monkeypatch):
    """Test nested directory paths."""
    monkeypatch.chdir(setup_mock_files)

    site_url = "https://example.com/"

    # Test nested directory
    assert (
        _convert_url_to_file_path(
            "https://example.com/nested/",
            site_url,
            setup_mock_files,
        )
        == "nested/index.md"
    )


def test_latest_directory(setup_mock_files, monkeypatch):
    """Test paths with 'latest' directory."""
    monkeypatch.chdir(setup_mock_files)

    site_url = "https://example.com/"

    # Test with and without latest/
    assert (
        _convert_url_to_file_path(
            "https://example.com/latest/guide.html",
            site_url,
            setup_mock_files,
        )
        == "latest/guide.md"
    )
    assert (
        _convert_url_to_file_path(
            "https://example.com/latest/index.html",
            site_url,
            setup_mock_files,
        )
        == "index.md"
    )


def test_locale_directory(setup_mock_files, monkeypatch):
    """Test paths with locale directory."""
    monkeypatch.chdir(setup_mock_files)

    site_url = "https://example.com/"

    # Test with and without locale
    assert (
        _convert_url_to_file_path(
            "https://example.com/en/about.html",
            site_url,
            setup_mock_files,
        )
        == "en/about.md"
    )
    assert (
        _convert_url_to_file_path(
            "https://example.com/en/non_locale.html",
            site_url,
            setup_mock_files,
        )
        == "non_locale.md"
    )
    assert (
        _convert_url_to_file_path(
            "https://example.com/en/nested/non_locale.html",
            site_url,
            setup_mock_files,
        )
        == "nested/non_locale.md"
    )


def test_invalid_urls(setup_mock_files, monkeypatch):
    """Test invalid URLs and non-existent files."""
    monkeypatch.chdir(setup_mock_files)

    site_url = "https://example.com/"

    # Test URL that doesn't match site_url
    assert (
        _convert_url_to_file_path(
            "https://different.com/page.html",
            site_url,
            setup_mock_files,
        )
        == ""
    )

    # Test non-existent file
    assert (
        _convert_url_to_file_path(
            "https://example.com/nonexistent.html",
            site_url,
            setup_mock_files,
        )
        == ""
    )
