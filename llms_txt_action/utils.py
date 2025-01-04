"""Utility functions for the llms-txt-action action."""

# %%
import logging
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from defusedxml import ElementTree as ET  # noqa: N817
from docling.datamodel.base_models import ConversionStatus
from docling.document_converter import DocumentConverter
from litellm import completion

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


def summarize_page(content: str, model_name: str) -> str:
    """Summarize the page content using the model.

    This would analyze the page content and generate a summary.

    Args:
    ----
        content (str): The content of the page to summarize
        model_name (str): Name of the model to use for summarization

    Returns:
    -------
        str: A static summary of the page

    """
    if os.getenv("MODEL_API_KEY"):
        response = completion(
            model=model_name,
            api_key=os.getenv("MODEL_API_KEY"),
            messages=[
                {
                    "content": "Summarize this into 1-line sentence packing information"
                    "for technical audience. Content: " + content,
                    "role": "user",
                },
            ],
        )
        logger.info("Response: %s", response)
        return response.choices[0].message.content
    # Extract largest heading from markdown content if present
    logger.info("No model API key found, using heading as summary")
    return extract_heading(content)


def extract_heading(content: str) -> str:
    """Extract the largest heading upto h3 from the given content."""
    heading_match = re.search(r"^#{1,3}\s+(.+)$", content, re.MULTILINE)
    logger.info("Heading match: %s", heading_match)
    if heading_match:
        return heading_match.group(1)
    return ""


def generate_docs_structure(
    docs_dir: str,
    sitemap_path: str,
    model_name: str,
) -> str:
    """Generate a documentation structure from a sitemap.xml file.

    Args:
    ----
        docs_dir (str): Path to the directory containing the documentation
        sitemap_path (str): Path to the sitemap.xml file
        model_name (str): Name of the model to use for summarization

    Returns:
    -------
        str: Markdown formatted documentation structure

    """
    # Parse the sitemap XML
    if not Path(f"{docs_dir}/{sitemap_path}").exists():
        msg = f"The sitemap file {docs_dir}/{sitemap_path} does not exist."
        raise FileNotFoundError(msg)
    tree = ET.parse(f"{docs_dir}/{sitemap_path}")
    root = tree.getroot()

    # Extract namespace
    ns = {"ns": root.tag.split("}")[0].strip("{")}

    # Start building the markdown content
    content = ["# Docs\n"]

    # Process each URL in the sitemap
    for url in root.findall(".//ns:url", ns):
        loc = url.find("ns:loc", ns).text
        """
        This doesnt call all cases. let me give more examples that needs to be handled.

        https://test.com/ -> index.md
        https://test.com/index.html -> index.md
        https://test.com/configuration/ -> configuration/index.md
        https://test.com/configuration/azure/ -> configuration/azure/index.md
        https://test.comen/configuration/auzre.html -> configuration/azure.md
        """
        # Convert URL to file path
        parsed_url = urlparse(loc)
        path = parsed_url.path.strip("/")

        # Handle different URL patterns
        if path in {"", "index.html"}:
            file_path = "index.md"
        elif path.endswith(".html"):
            # Remove .html and convert to .md
            file_path = f"{path[:-5]}.md"
        else:
            # For paths ending in / or no extension, append index.md
            file_path = f"{path}/index.md"
        # Generate a summary for the page
        try:
            with Path(f"{docs_dir}/{file_path}").open() as f:
                markdown_content = f.read()
        except FileNotFoundError:
            # Try without locale path by removing first directory if it's 2 characters
            file_path_parts = file_path.split("/")

            file_path_no_locale = (
                "/".join(file_path_parts[1:])
                if len(file_path_parts) > 1 and len(file_path_parts[0]) == 2  # noqa: PLR2004
                else file_path
            )
            with Path(f"{docs_dir}/{file_path_no_locale}").open() as f:
                markdown_content = f.read()
        summary = summarize_page(markdown_content, model_name)

        # Create the markdown link entry
        page_title = loc.rstrip("/").split("/")[-1].replace("-", " ").title()
        content.append(f"- [{page_title}]({loc}): {summary}")

    # Join all lines with newlines
    return "\n".join(content)


# %%


def concatenate_markdown_files(markdown_files: list, output_file: str):
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
