"""Utility functions for the llms-txt-action action."""

# %%
import logging
from pathlib import Path

from defusedxml import ElementTree as ET  # noqa: N817
from docling.datamodel.base_models import ConversionStatus
from docling.document_converter import DocumentConverter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# %%
def html_to_markdown(input_file: Path) -> str:
    """Converts HTML content to Markdown.

    Removes content before the first heading efficiently.

    Args:
    ----
        input_file (Path): The path to the HTML file to convert.

    Returns:
    -------
        str: The Markdown content of the input file.

    """  # noqa: D401
    doc_converter = DocumentConverter()
    conversion_result = doc_converter.convert(input_file)
    print(conversion_result)
    print("selvam")
    logger.info(conversion_result)
    if conversion_result.status == ConversionStatus.SUCCESS:
        markdown_content = conversion_result.document.export_to_markdown()
        # Fast string search for first heading using find()
        index = markdown_content.find("\n#")
        return markdown_content[index + 1 :] if index >= 0 else markdown_content
    msg = f"Failed to convert {input_file}: {conversion_result.errors}"
    raise RuntimeError(msg)


def convert_html_to_markdown(input_path: str) -> list:
    """Recursively converts all HTML files in the given directory.

    to Markdown files and collects the paths of the generated Markdown files.

    Args:
    ----
        input_path (str): The path to the directory containing HTML files

    Returns:
    -------
        list: A list of paths to the generated Markdown files

    Raises:
    ------
        ValueError: If the input path is not a directory

    """
    # Configure logging

    input_dir = Path(input_path)
    if not input_dir.is_dir():
        msg = f"The input path {input_path} is not a directory."
        raise ValueError(msg)

    # Track conversion statistics
    success_count = 0
    failure_count = 0
    markdown_files = []

    # Recursively process all HTML files
    for html_file in input_dir.rglob("*.html"):
        try:
            logger.info("Converting %s", html_file)

            # Convert to markdown
            markdown_content = html_to_markdown(html_file)

            # Create output markdown file in the same directory as the HTML file
            markdown_file = html_file.with_suffix(".md")

            # Create parent directories if they don't exist
            markdown_file.parent.mkdir(parents=True, exist_ok=True)

            with Path(markdown_file).open("w", encoding="utf-8") as file:
                file.write(markdown_content)

            success_count += 1
            markdown_files.append(markdown_file)
            logger.info("Successfully converted %s to %s", html_file, markdown_file)

        except Exception:
            failure_count += 1
            logger.exception("Failed to convert %s", html_file)

    # Log summary
    logger.info(
        "Conversion complete: %d successful, %d failed",
        success_count,
        failure_count,
    )
    return markdown_files


# %%


def summarize_page(url: str) -> str:  # noqa: ARG001
    """Dummy function that returns a static summary for each page.

    This would analyze the page content and generate a summary.

    Args:
    ----
        url (str): The URL of the page to summarize

    Returns:
    -------
        str: A static summary of the page

    """  # noqa: D401
    return "This is a placeholder summary for the documentation page."


def generate_docs_structure(sitemap_path: str) -> str:
    """Generates a documentation structure from a sitemap.xml file.

    Args:
    ----
        sitemap_path (str): Path to the sitemap.xml file

    Returns:
    -------
        str: Markdown formatted documentation structure

    """  # noqa: D401
    # Parse the sitemap XML
    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    # Extract namespace
    ns = {"ns": root.tag.split("}")[0].strip("{")}

    # Start building the markdown content
    content = ["# Docling Documentation\n\n## Docs\n"]

    # Process each URL in the sitemap
    for url in root.findall(".//ns:url", ns):
        loc = url.find("ns:loc", ns).text

        # Skip the main page
        if loc.endswith("/docling/"):
            continue

        # Generate a summary for the page
        summary = summarize_page(loc)

        # Create the markdown link entry
        page_title = loc.rstrip("/").split("/")[-1].replace("-", " ").title()
        content.append(f"- [{page_title}]({loc}): {summary}")

    # Join all lines with newlines
    return "\n".join(content)


# %%


def concatenate_markdown_files(markdown_files, output_file):
    """Concatenates multiple markdown files into a single file.

    Args:
    ----
        markdown_files (list): List of paths to markdown files
        output_file (str): Path to the output file

    """
    with Path(output_file).open("w") as outfile:
        for file_path in markdown_files:
            with Path(file_path).open() as infile:
                outfile.write(infile.read())
                outfile.write("\n\n")
