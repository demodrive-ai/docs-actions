"""Script to generate markdown files and llms.txt from HTML documentation."""

import argparse
import logging
import os
from pathlib import Path

from .utils import (
    concatenate_markdown_files,
    convert_html_to_markdown,
    generate_docs_structure,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def str2bool(v):
    """Convert string to boolean."""
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if v.lower() in ("no", "false", "f", "n", "0"):
        return False
    msg = "Boolean value expected."
    raise argparse.ArgumentTypeError(msg)


def generate_documentation(  # noqa: PLR0913
    docs_dir: str = "site",
    sitemap_path: str = "sitemap.xml",
    generate_md_files: bool | None = None,
    generate_llms_txt: bool | None = None,
    generate_llms_full_txt: bool | None = None,
    llms_txt_name: str = "llms.txt",
    llms_full_txt_name: str = "llms_full.txt",
) -> list[str]:
    """Generate markdown and llms.txt files from HTML documentation.

    Args:
    ----
        docs_dir: Directory containing HTML documentation
        sitemap_path: Path to the sitemap.xml file relative to docs_dir
        generate_md_files: Whether to keep generated markdown files
        generate_llms_txt: Whether to generate llms.txt
        generate_llms_full_txt: Whether to generate full llms.txt
        llms_txt_name: Name of the llms.txt file
        llms_full_txt_name: Name of the full llms.txt file

    Returns:
    -------
        List of generated markdown file paths

    """
    docs_dir = docs_dir.rstrip("/")
    logger.info("Starting Generation at folder - %s", docs_dir)

    logger.info("Generating MD files for all HTML files at folder - %s", docs_dir)
    markdown_files = convert_html_to_markdown(docs_dir)

    # Set defaults if None
    generate_md_files = True if generate_md_files is None else generate_md_files
    generate_llms_txt = True if generate_llms_txt is None else generate_llms_txt
    generate_llms_full_txt = (
        True if generate_llms_full_txt is None else generate_llms_full_txt
    )

    if generate_llms_txt:
        with Path(f"{docs_dir}/{llms_txt_name}").open("w") as f:
            f.write(generate_docs_structure(f"{docs_dir}/{sitemap_path}"))
        logger.info("llms.txt file generated at %s", f"{docs_dir}/{llms_txt_name}")

    if generate_llms_full_txt:
        logger.info("Generating llms.txt file")
        concatenate_markdown_files(
            markdown_files,
            f"{docs_dir}/{llms_full_txt_name}",
        )
        logger.info(
            "llms_full.txt file generated at %s",
            f"{docs_dir}/{llms_full_txt_name}",
        )

    if not generate_md_files:
        logger.info("Deleting MD files as generate_md_files is set to False")
        for file in markdown_files:
            Path(file).unlink()
        logger.info("MD files deleted.")

    logger.info("Generation completed.")
    return markdown_files


def main():
    """Parse arguments and run generate_documentation."""
    parser = argparse.ArgumentParser(
        description="Generate markdown and llms.txt files from HTML documentation.",
    )
    parser.add_argument(
        "--docs-dir",
        default=os.environ.get("INPUT_DOCS_DIR", "site"),
        help="Directory containing HTML documentation [default: site]",
    )
    parser.add_argument(
        "--generate-md-files",
        type=str2bool,
        default=os.environ.get("INPUT_GENERATE_MD_FILES", "true").lower() == "true",
        help="Whether to keep generated markdown files [default: true]",
    )
    parser.add_argument(
        "--generate-llms-txt",
        type=str2bool,
        default=os.environ.get("INPUT_GENERATE_LLMS_TXT", "true").lower() == "true",
        help="Whether to generate llms.txt [default: true]",
    )
    parser.add_argument(
        "--generate-llms-full-txt",
        type=str2bool,
        default=os.environ.get("INPUT_GENERATE_LLMS_FULL_TXT", "true").lower()
        == "true",
        help="Whether to generate full llms.txt [default: true]",
    )
    parser.add_argument(
        "--llms-txt-name",
        default=os.environ.get("INPUT_LLMS_TXT_NAME", "llms.txt"),
        help="Name of the llms.txt file [default: llms.txt]",
    )
    parser.add_argument(
        "--llms-full-txt-name",
        default=os.environ.get("INPUT_LLMS_FULL_TXT_NAME", "llms_full.txt"),
        help="Name of the full llms.txt file [default: llms_full.txt]",
    )
    parser.add_argument(
        "--sitemap-path",
        default=os.environ.get("INPUT_SITEMAP_PATH", "sitemap.xml"),
        help="Path relative to docs_dir to the sitemap.xml file [default: sitemap.xml]",
    )

    args = parser.parse_args()
    generate_documentation(
        docs_dir=args.docs_dir,
        sitemap_path=args.sitemap_path,
        generate_md_files=args.generate_md_files,
        generate_llms_txt=args.generate_llms_txt,
        generate_llms_full_txt=args.generate_llms_full_txt,
        llms_txt_name=args.llms_txt_name,
        llms_full_txt_name=args.llms_full_txt_name,
    )


if __name__ == "__main__":
    main()
