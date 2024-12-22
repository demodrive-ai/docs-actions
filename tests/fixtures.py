"""Test fixtures for docs-actions."""

import pytest

from docs_actions.api_client import FirecrawlClient


@pytest.fixture
def mock_crawl_response():
    """Sample crawl response fixture."""
    return {
        "success": True,
        "status": "completed",
        "completed": 2,
        "total": 2,
        "creditsUsed": 2,
        "expiresAt": "2024-12-23T16:12:50.000Z",
        "data": [
            {
                "html": '<!DOCTYPE html><html lang="en"><body class="__variable_1e4310 __variable_c3aa02 antialiased min-h-screen dark bg-background text-foreground">...</body></html>',
                "markdown": "Make your docs\n\nError Proof\n\nAI find bugs and generates usability report for your documentation...",
                "metadata": {
                    "url": "https://www.demodrive.tech/",
                    "title": "DemoDrive - Documentation Testing",
                    "language": "en",
                    "description": "AI-powered documentation testing and improvement platform",
                },
            },
            {
                "html": '<!DOCTYPE html><html lang="en"><body class="__variable_1e4310 __variable_c3aa02 antialiased min-h-screen dark bg-background text-foreground">...</body></html>',
                "markdown": "Simple pricing\n\nJust have one pricing plan for you...",
                "metadata": {
                    "url": "https://www.demodrive.tech/pricing",
                    "title": "DemoDrive - Documentation Testing",
                    "language": "en",
                    "description": "AI-powered documentation testing and improvement platform",
                },
            },
        ],
    }


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory."""
    return tmp_path / "crawl_output"


@pytest.fixture
def client(temp_output_dir):
    """Create a FirecrawlClient instance with test configuration."""
    return FirecrawlClient("test-api-key", temp_output_dir)
