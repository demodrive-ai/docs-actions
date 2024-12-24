# %%
import logging
from pathlib import Path
from docling.datamodel.base_models import ConversionStatus
from docling.document_converter import DocumentConverter
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# %%
def html_to_markdown(input_file: Path) -> str:
    """
    Converts HTML content to Markdown using Docling's document converter and removes
    content before the first heading efficiently.
    """
    doc_converter = DocumentConverter()
    conversion_result = doc_converter.convert(input_file)

    if conversion_result.status == ConversionStatus.SUCCESS:
        markdown_content = conversion_result.document.export_to_markdown()
        # Fast string search for first heading using find()
        index = markdown_content.find("\n#")
        return markdown_content[index + 1 :] if index >= 0 else markdown_content
    else:
        raise RuntimeError(
            f"Failed to convert {input_file}: {conversion_result.errors}"
        )


def convert_html_to_markdown(input_path: str) -> list:
    """
    Recursively converts all HTML files in the given directory and its subdirectories
    to Markdown files and collects the paths of the generated Markdown files.

    Args:
        input_path (str): The path to the directory containing HTML files

    Returns:
        list: A list of paths to the generated Markdown files

    Raises:
        ValueError: If the input path is not a directory
    """
    # Configure logging

    input_dir = Path(input_path)
    if not input_dir.is_dir():
        raise ValueError(f"The input path {input_path} is not a directory.")

    # Track conversion statistics
    success_count = 0
    failure_count = 0
    markdown_files = []

    # Recursively process all HTML files
    for html_file in input_dir.rglob("*.html"):
        try:
            logger.info(f"Converting {html_file}")

            # Convert to markdown
            markdown_content = html_to_markdown(html_file)

            # Create output markdown file in the same directory as the HTML file
            markdown_file = html_file.with_suffix(".md")

            # Create parent directories if they don't exist
            markdown_file.parent.mkdir(parents=True, exist_ok=True)

            with open(markdown_file, "w", encoding="utf-8") as file:
                file.write(markdown_content)

            success_count += 1
            markdown_files.append(markdown_file)
            logger.info(f"Successfully converted {html_file} to {markdown_file}")

        except Exception as e:
            failure_count += 1
            logger.error(f"Failed to convert {html_file}: {str(e)}")

    # Log summary
    logger.info(
        f"Conversion complete: {success_count} successful, {failure_count} failed"
    )
    return markdown_files


# Example usage
# markdown_files = convert_html_to_markdown(
#     "/Users/nehiljain/code/playground-rag/docling-clone/site/"
# )

# %%


def summarize_page(url: str) -> str:
    """
    Dummy function that returns a static summary for each page.
    In a real implementation, this would analyze the page content and generate a summary.

    Args:
        url (str): The URL of the page to summarize

    Returns:
        str: A static summary of the page
    """
    return "This is a placeholder summary for the documentation page."


def generate_docs_structure(sitemap_path: str) -> str:
    """
    Generates a documentation structure from a sitemap.xml file.

    Args:
        sitemap_path (str): Path to the sitemap.xml file

    Returns:
        str: Markdown formatted documentation structure
    """

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


# Example usage:
# sitemap_path = "/Users/spalanimalai/projects/llms-txt-action/typer/site/sitemap.xml"
# docs_structure = generate_docs_structure(sitemap_path)
# output_path = sitemap_path.replace("sitemap.xml", "llms.txt")
# with open(output_path, "w") as file:
#     file.write(docs_structure)

# %%


def concatenate_markdown_files(markdown_files, output_file):
    """
    Concatenates multiple markdown files into a single file.

    Args:
        markdown_files (list): List of paths to markdown files
        output_file (str): Path to the output file
    """
    with open(output_file, "w") as outfile:
        for file_path in markdown_files:
            with open(file_path, "r") as infile:
                outfile.write(infile.read())
                outfile.write("\n\n")  # Add a newline between files for separation


# output_filepath = sitemap_path.replace("sitemap.xml", "llms-full.txt")

# concatenate_markdown_files(markdown_files, output_filepath)
