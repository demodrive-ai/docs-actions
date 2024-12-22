"""API client for interacting with Firecrawl."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from firecrawl import FirecrawlApp


class FirecrawlClient:
    """Client for making requests to Firecrawl."""

    def __init__(self, api_key: str, output_dir: Path | None = None) -> None:
        """Initialize the Firecrawl client.

        Args:
            api_key: Firecrawl API key
            output_dir: Directory to save crawled data (default: docs/crawled)

        """
        self.app = FirecrawlApp(api_key=api_key)
        self.output_dir = output_dir or Path("docs/crawled")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def crawl(self, url: str, limit: int = 10) -> dict[str, Any]:
        """Crawl a website and save the results.

        Args:
            url: Website URL to crawl
            limit: Maximum number of pages to crawl

        Returns:
            Dict[str, Any]: Crawl status and results

        """
        crawl_status = self.app.crawl_url(
            url,
            params={"limit": limit, "scrapeOptions": {"formats": ["markdown", "html"]}},
            poll_interval=30,
        )

        # Save the crawl results if successful
        if crawl_status.get("success"):
            self._save_crawled_data(crawl_status)

        return crawl_status

    def _save_crawled_data(self, crawl_data: dict[str, Any]) -> None:
        """Save crawled data to files.

        Args:
            crawl_data: Crawl results from Firecrawl

        """
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
        crawl_dir = self.output_dir / timestamp
        crawl_dir.mkdir(exist_ok=True)

        # Prepare content for llms-full.txt
        llms_content = []

        # Save pages
        for i, page in enumerate(crawl_data.get("data", [])):
            # Save HTML content
            html_file = crawl_dir / f"page_{i}_html.html"
            with html_file.open("w", encoding="utf-8") as f:
                f.write(page.get("html", ""))

            # Save Markdown content
            md_file = crawl_dir / f"page_{i}_md.md"
            with md_file.open("w", encoding="utf-8") as f:
                f.write(page.get("markdown", ""))

            # Save metadata
            meta_file = crawl_dir / f"page_{i}_meta.json"
            with meta_file.open("w", encoding="utf-8") as f:
                json.dump(page.get("metadata", {}), f, indent=2)

            # Append formatted content for llms-full.txt
            metadata = page.get("metadata", {})
            llms_content.append(
                "# ["
                f"{metadata.get('title', 'Untitled')}"
                "]("
                f"{metadata.get('url', '')}"
                ")\n\n"
                f"{page.get('markdown', '')}\n\n",
            )

        # Save combined markdown content
        llms_file = crawl_dir / "llms-full.txt"
        with llms_file.open("w", encoding="utf-8") as f:
            f.write("".join(llms_content))

        # Save crawl metadata
        meta_file = crawl_dir / "crawl_metadata.json"
        with meta_file.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": timestamp,
                    "success": crawl_data.get("success"),
                    "status": crawl_data.get("status"),
                    "total_pages": crawl_data.get("total"),
                    "completed_pages": crawl_data.get("completed"),
                    "credits_used": crawl_data.get("creditsUsed"),
                    "expires_at": crawl_data.get("expiresAt"),
                },
                f,
                indent=2,
            )
