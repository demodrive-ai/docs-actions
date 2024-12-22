#!/usr/bin/env python3
"""CLI script for crawling documentation websites."""

import argparse
import os
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .api_client import FirecrawlClient

console = Console()


def main():
    """Run the crawler CLI."""
    parser = argparse.ArgumentParser(description="Crawl documentation websites")
    parser.add_argument("--url", required=True, help="URL to crawl")
    parser.add_argument("--limit", type=int, default=100, help="Maximum pages to crawl")
    parser.add_argument(
        "--output",
        type=str,
        default="docs/crawled",
        help="Output directory",
    )
    parser.add_argument(
        "--formats",
        type=str,
        default="html,markdown,metadata",
        help="Output formats (comma-separated)",
    )

    args = parser.parse_args()

    # Get API key from environment
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        console.print(
            Panel("[red]❌ FIRECRAWL_API_KEY environment variable not set[/]"),
        )
        return 1

    # Setup output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize client
    client = FirecrawlClient(api_key, output_dir)

    try:
        # Run crawl
        console.print(f"\n[bold blue]🕷️ Crawling[/] {args.url}")
        result = client.crawl(args.url, limit=args.limit)

        # Display results
        table = Table(
            title="🔍 Crawl Results",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Success", "✅" if result.get("success") else "❌")
        table.add_row("Status", result.get("status"))
        table.add_row("Pages", f"{result.get('completed')}/{result.get('total')}")
        table.add_row("Credits Used", str(result.get("creditsUsed")))
        console.print(table)

        if not result.get("success"):
            console.print(f"\n[red]❌ Crawl failed: {result.get('error')}[/]")
            return 1

        # Show output summary
        crawl_dirs = list(output_dir.glob("*"))
        if not crawl_dirs:
            console.print("\n[red]❌ No output generated[/]")
            return 1

        latest_dir = max(crawl_dirs, key=lambda p: p.stat().st_mtime)
        console.print("\n[bold green]✅ Crawl completed successfully![/]")
        console.print(f"[bold blue]📁 Output directory:[/] {latest_dir}")
        return 0

    except (OSError, ValueError, KeyError) as e:
        console.print(f"\n[red]❌ Error: {e!s}[/]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
