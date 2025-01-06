"""Script to generate markdown files and llms.txt from HTML documentation."""
# ruff: noqa: UP007

import argparse
import logging
import os
from pathlib import Path
from typing import Optional

from .utils import (
    concatenate_markdown_files,
    generate_docs_structure,
    html_folder_to_markdown,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def str2bool(v: str) -> bool:
    """Convert a string to a boolean."""
    return v.lower() in ("yes", "true", "t", "1")


def generate_documentation(  # noqa: PLR0913
    docs_dir: str,
    sitemap_path: str,
    skip_md_files: Optional[bool],
    skip_llms_txt: Optional[bool],
    skip_llms_full_txt: Optional[bool],
    llms_txt_name: str,
    llms_full_txt_name: str,
    model_name: str,
) -> list[str]:
    """Generate markdown and llms.txt files from HTML documentation.

    Args:
    ----
        docs_dir: Directory containing HTML documentation
        sitemap_path: Path to the sitemap.xml file relative to docs_dir
        skip_md_files: Whether to skip generation of markdown files
        skip_llms_txt: Whether to skip llms.txt generation
        skip_llms_full_txt: Whether to skip full llms.txt generation
        llms_txt_name: Name of the llms.txt file
        llms_full_txt_name: Name of the full llms.txt file
        model_name: Name of the model to use for summarization

    Returns:
    -------
        List of generated markdown file paths

    """
    docs_dir = docs_dir.rstrip("/")
    logger.info("Starting Generation at folder - %s", docs_dir)

    logger.info("Generating MD files for all HTML files at folder - %s", docs_dir)
    markdown_files = html_folder_to_markdown(docs_dir)

    # Set defaults if None
    skip_md_files = False if skip_md_files is None else skip_md_files
    skip_llms_txt = False if skip_llms_txt is None else skip_llms_txt
    skip_llms_full_txt = False if skip_llms_full_txt is None else skip_llms_full_txt

    if not skip_llms_txt:
        with Path(f"{docs_dir}/{llms_txt_name}").open("w") as f:
            try:
                f.write(
                    generate_docs_structure(
                        docs_dir,
                        sitemap_path,
                        model_name,
                    ),
                )
                logger.info(
                    "llms.txt file generated at %s",
                    f"{docs_dir}/{llms_txt_name}",
                )
            except FileNotFoundError:
                logger.exception(
                    "Failed to generate llms.txt file",
                )

    if not skip_llms_full_txt:
        concatenate_markdown_files(
            markdown_files,
            f"{docs_dir}/{llms_full_txt_name}",
        )
        logger.info(
            "llms-full.txt file generated at %s",
            f"{docs_dir}/{llms_full_txt_name}",
        )

    if skip_md_files:
        logger.info("Deleting generated .md files as skip_md_files is set to False")
        for file in markdown_files:
            Path(file).unlink()
        logger.info(".md files deleted.")

    logger.info("Docs are LLM friendly now! 🎉")
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
        "--skip-md-files",
        action="store_true",
        default=str2bool(os.environ.get("INPUT_SKIP_MD_FILES", "false")),
        help="Skip generation of markdown files",
    )
    parser.add_argument(
        "--skip-llms-txt",
        action="store_true",
        default=str2bool(os.environ.get("INPUT_SKIP_LLMS_TXT", "false")),
        help="Skip llms.txt file generation",
    )
    parser.add_argument(
        "--skip-llms-full-txt",
        action="store_true",
        default=str2bool(os.environ.get("INPUT_SKIP_LLMS_FULL_TXT", "false")),
        help="Skip full llms.txt file generation",
    )
    parser.add_argument(
        "--llms-txt-name",
        default=os.environ.get("INPUT_LLMS_TXT_NAME", "llms.txt"),
        help="Name of the llms.txt file [default: llms.txt]",
    )
    parser.add_argument(
        "--llms-full-txt-name",
        default=os.environ.get("INPUT_LLMS_FULL_TXT_NAME", "llms-full.txt"),
        help="Name of the full llms.txt file [default: llms-full.txt]",
    )
    parser.add_argument(
        "--sitemap-path",
        default=os.environ.get("INPUT_SITEMAP_PATH", "sitemap.xml"),
        help="Path relative to docs_dir to the sitemap.xml file [default: sitemap.xml]",
    )
    parser.add_argument(
        "--model-name",
        default=os.environ.get("INPUT_MODEL_NAME", "gpt-4o"),
        help="Name of the model to use for summarization [default: gpt-4o]",
    )

    args = parser.parse_args()
    logger.info("input args: %s", args)

    generate_documentation(
        docs_dir=args.docs_dir,
        sitemap_path=args.sitemap_path,
        skip_md_files=args.skip_md_files,
        skip_llms_txt=args.skip_llms_txt,
        skip_llms_full_txt=args.skip_llms_full_txt,
        llms_txt_name=args.llms_txt_name,
        llms_full_txt_name=args.llms_full_txt_name,
        model_name=args.model_name,
    )


if __name__ == "__main__":
    main()
