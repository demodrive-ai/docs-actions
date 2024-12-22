"""Tests for the API client."""

import json
from unittest.mock import Mock

import pytest

EXPECTED_PAGES = 2


def test_crawl_success(client, mock_crawl_response, temp_output_dir):
    """Test successful crawl and file saving."""
    client.app.crawl_url = Mock(return_value=mock_crawl_response)
    result = client.crawl("https://demodrive.tech", limit=2)

    # Verify API response
    assert result["success"] is True
    assert result["status"] == "completed"
    assert result["completed"] == EXPECTED_PAGES

    # Check saved files
    crawl_dirs = list(temp_output_dir.glob("*"))
    assert len(crawl_dirs) == 1
    crawl_dir = crawl_dirs[0]

    # Verify metadata
    meta_file = crawl_dir / "crawl_metadata.json"
    assert meta_file.exists()
    with meta_file.open() as f:
        meta = json.load(f)
        assert meta["success"] is True
        assert meta["total_pages"] == EXPECTED_PAGES
        assert meta["completed_pages"] == EXPECTED_PAGES

    # Verify page files exist
    for i in range(2):
        assert (crawl_dir / f"page_{i}_html.html").exists()
        assert (crawl_dir / f"page_{i}_md.md").exists()
        assert (crawl_dir / f"page_{i}_meta.json").exists()

        # Verify metadata content
        with (crawl_dir / f"page_{i}_meta.json").open() as f:
            meta = json.load(f)
            assert meta["title"] == "DemoDrive - Documentation Testing"
            assert meta["language"] == "en"

    # Verify llms-full.txt exists and has correct content
    llms_file = crawl_dir / "llms-full.txt"
    assert llms_file.exists()

    with llms_file.open() as f:
        content = f.read()
        # Check first page
        assert (
            "# [DemoDrive - Documentation Testing](https://www.demodrive.tech/)"
            in content
        )
        assert "Make your docs\n\nError Proof" in content
        # Check second page
        assert (
            "# [DemoDrive - Documentation Testing](https://www.demodrive.tech/pricing)"
            in content
        )
        assert "Simple pricing\n\nJust have one pricing plan" in content


def test_crawl_failure(client):
    """Test crawl failure handling."""
    error_response = {"success": False, "status": "failed", "error": "Invalid URL"}

    client.app.crawl_url = Mock(return_value=error_response)
    result = client.crawl("https://invalid-url", limit=2)
    assert result["success"] is False
    assert result["status"] == "failed"

    # Verify no files were saved
    assert not list(client.output_dir.glob("*"))


def test_crawl_exception(client):
    """Test exception handling during crawl."""
    client.app.crawl_url = Mock(side_effect=Exception("API Error"))
    with pytest.raises(Exception) as exc_info:
        client.crawl("https://example.com", limit=2)
    assert str(exc_info.value) == "API Error"
