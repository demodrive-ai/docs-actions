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


def generate_documentation(  # noqa: PLR0913
    docs_dir: str,
    sitemap_path: str,
    skip_md_files: bool | None,
    skip_llms_txt: bool | None,
    skip_llms_full_txt: bool | None,
    llms_txt_name: str,
    llms_full_txt_name: str,
    model_name: str,
    model_max_tokens: int,
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
        model_max_tokens: Max tokens for the model

    Returns:
    -------
        List of generated markdown file paths

    """
    docs_dir = docs_dir.rstrip("/")
    logger.info("Starting Generation at folder - %s", docs_dir)

    logger.info("Generating MD files for all HTML files at folder - %s", docs_dir)
    markdown_files = convert_html_to_markdown(docs_dir)

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
                        model_max_tokens,
                    ),
                )
                logger.info(
                    "llms.txt file generated at %s",
                    f"{docs_dir}/{llms_txt_name}",
                )
            except FileNotFoundError:
                logger.exception(
                    "Could not find sitemap file at %s",
                    f"{docs_dir}/{sitemap_path}",
                )
                raise

    if not skip_llms_full_txt:
        logger.info("Generating llms.txt file")
        concatenate_markdown_files(
            markdown_files,
            f"{docs_dir}/{llms_full_txt_name}",
        )
        logger.info(
            "llms_full.txt file generated at %s",
            f"{docs_dir}/{llms_full_txt_name}",
        )

    if skip_md_files:
        logger.info("Deleting MD files as skip_md_files is set to False")
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
        "--skip-md-files",
        action="store_true",
        help="Skip generation of markdown files",
    )
    parser.add_argument(
        "--skip-llms-txt",
        action="store_true",
        help="Skip llms.txt file generation",
    )
    parser.add_argument(
        "--skip-llms-full-txt",
        action="store_true",
        help="Skip full llms.txt file generation",
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
    parser.add_argument(
        "--model-name",
        default=os.environ.get("INPUT_MODEL_NAME", "gpt-4o"),
        help="Name of the model to use for summarization [default: gpt-4o]",
    )
    parser.add_argument(
        "--model-max-tokens",
        default=int(os.environ.get("INPUT_MODEL_MAX_TOKENS", "2000")),
        help="Max tokens for the model [default: 2000]",
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
        model_max_tokens=args.model_max_tokens,
    )


if __name__ == "__main__":
    main()
