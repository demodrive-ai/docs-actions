import json
import os
import shutil
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from docs_actions.api_client import FirecrawlClient

console = Console()


def get_file_stats(file_path):
    """Get file stats in lines and KB."""
    size_kb = file_path.stat().st_size / 1024
    with file_path.open() as f:
        line_count = sum(1 for _ in f)
    return f"{line_count:,} lines ({size_kb:.1f} KB)"


def test_crawl():
    """Test crawling with real API credentials."""
    # Get API key from environment variable
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        console.print(
            Panel("[yellow]⚠️  FIRECRAWL_API_KEY environment variable not set[/]"),
        )
        console.print(
            "[blue]Run with: [green]FIRECRAWL_API_KEY=your-key python tests/test_crawl_local.py[/][/]",
        )
        return

    # Setup test output directory
    output_dir = Path("test_output")
    if output_dir.exists():
        shutil.rmtree(output_dir)

    client = FirecrawlClient(api_key, output_dir)

    try:
        # Test crawling a small site
        result = client.crawl("https://demodrive.tech/", limit=2)

        # Create results table
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

        if result.get("success"):
            crawl_dirs = list(output_dir.glob("*"))
            if not crawl_dirs:
                console.print("\n[red]❌ No crawl directory created[/]")
                return

            latest_dir = max(crawl_dirs, key=lambda p: p.stat().st_mtime)
            console.print(f"\n[bold blue]💾 Saved Files[/] ([green]{latest_dir}[/])")

            # Print metadata
            meta_file = latest_dir / "crawl_metadata.json"
            if meta_file.exists():
                with meta_file.open() as f:
                    meta = json.load(f)
                console.print("\n[bold blue]📊 Crawl Metadata:[/]")
                syntax = Syntax(json.dumps(meta, indent=2), "json", theme="monokai")
                console.print(syntax)

            # Count and display files
            html_files = list(latest_dir.glob("*_html.html"))
            md_files = list(latest_dir.glob("*_md.md"))
            meta_files = list(latest_dir.glob("*_meta.json"))
            llms_file = latest_dir / "llms-full.txt"

            files_table = Table(
                title="📁 File Counts",
                show_header=True,
                header_style="bold magenta",
            )
            files_table.add_column("File Type", style="cyan")
            files_table.add_column("Count", style="green")
            files_table.add_column("Size", style="yellow")

            if html_files:
                files_table.add_row(
                    "HTML",
                    str(len(html_files)),
                    get_file_stats(html_files[0]),
                )
            if md_files:
                files_table.add_row(
                    "Markdown",
                    str(len(md_files)),
                    get_file_stats(md_files[0]),
                )
            if meta_files:
                files_table.add_row(
                    "Metadata",
                    str(len(meta_files)),
                    get_file_stats(meta_files[0]),
                )
            if llms_file.exists():
                files_table.add_row("LLMs Full", "1", get_file_stats(llms_file))

                # Show preview of llms-full.txt
                with llms_file.open() as f:
                    content = "\n".join(f.readlines()[:5])
                    console.print(
                        "\n[bold blue]📖 First few lines of llms-full.txt:[/]",
                    )
                    syntax = Syntax(content, "markdown", theme="monokai")
                    console.print(Panel(syntax))
            else:
                console.print("[red]❌ llms-full.txt not found[/]")

            console.print(files_table)
            console.print("\n[bold green]✅ Test completed successfully![/]")
        else:
            console.print(f"\n[red]❌ Crawl failed: {result.get('error')}[/]")

    except Exception as e:
        console.print(f"\n[red]❌ Error during test: {e!s}[/]")


if __name__ == "__main__":
    test_crawl()
