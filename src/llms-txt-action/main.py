import os
from utils import concatenate_markdown_files, convert_html_to_markdown
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    logger.info("Starting Generation....")
    docs_dir = os.environ.get("INPUT_DOCS_DIR", "site").lstrip("/")
    generate_md_files = os.environ.get("INPUT_GENERATE_MD_FILES", "true")
    generate_llms_txt = os.environ.get("INPUT_GENERATE_LLMS_TXT", "true")
    llms_txt_name = os.environ.get("INPUT_LLMS_TXT_NAME", "llms.txt")
    poetry_version = os.environ.get("INPUT_POETRY_VERSION", "latest")

    logger.info("Generating MD files....")
    markdown_files = convert_html_to_markdown(docs_dir)

    if generate_llms_txt == "true":
        logger.info("Generating LLMS.txt file....")
        concatenate_markdown_files(
            markdown_files,
            f"{docs_dir}/{llms_txt_name}",
        )
        logger.info(f"LLMS.txt file generated at {docs_dir}/{llms_txt_name}.")

    if generate_md_files != "true":
        logger.info("Deleting MD files....")
        # delete all md files
        for file in markdown_files:
            os.remove(file)
        logger.info("MD files deleted.")
    logger.info("Generation completed.")
