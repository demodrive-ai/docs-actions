"""Test the entrypoint module."""

import os
from unittest.mock import patch

import pytest

from llms_txt_action.entrypoint import main, str2bool


@pytest.mark.parametrize(
    ("input_str", "expected"),
    [
        ("yes", True),
        ("YES", True),
        ("true", True),
        ("TRUE", True),
        ("t", True),
        ("T", True),
        ("1", True),
        ("no", False),
        ("false", False),
        ("f", False),
        ("0", False),
        ("random", False),
        ("", False),
    ],
)
def test_str2bool(input_str: str, expected: bool) -> None:  # noqa: FBT001
    """Test str2bool function with various inputs."""
    assert str2bool(input_str) == expected  # noqa: S101


@pytest.fixture
def mock_generate_documentation():
    """Mock the generate_documentation function."""
    with patch("llms_txt_action.entrypoint.generate_documentation") as mock:
        yield mock


def test_default_arguments(mock_generate_documentation):
    """Test that default values are used when no arguments are provided."""
    with patch("sys.argv", ["script"]):
        main()

    mock_generate_documentation.assert_called_once_with(
        docs_dir="site",
        sitemap_path="sitemap.xml",
        skip_md_files=False,
        skip_llms_txt=False,
        skip_llms_full_txt=False,
        llms_txt_name="llms.txt",
        llms_full_txt_name="llms-full.txt",
        model_name="gpt-4o",
    )


def test_cli_arguments(mock_generate_documentation):
    """Test that CLI arguments override default values."""
    test_args = [
        "script",
        "--docs-dir",
        "custom_docs",
        "--skip-md-files",
        "--llms-txt-name",
        "custom.txt",
        "--model-name",
        "gpt-3.5",
    ]

    with patch("sys.argv", test_args):
        main()

    mock_generate_documentation.assert_called_once_with(
        docs_dir="custom_docs",
        sitemap_path="sitemap.xml",  # default unchanged
        skip_md_files=True,
        skip_llms_txt=False,  # default unchanged
        skip_llms_full_txt=False,  # default unchanged
        llms_txt_name="custom.txt",
        llms_full_txt_name="llms-full.txt",  # default unchanged
        model_name="gpt-3.5",
    )


def test_environment_variables(mock_generate_documentation):
    """Test that environment variables override CLI arguments."""
    env_vars = {
        "INPUT_DOCS_DIR": "env_docs",
        "INPUT_SKIP_MD_FILES": "true",
        "INPUT_SKIP_LLMS_TXT": "true",
        "INPUT_LLMS_TXT_NAME": "env.txt",
        "INPUT_MODEL_NAME": "gpt-4",
    }

    with patch.dict(os.environ, env_vars), patch("sys.argv", ["script"]):
        main()

    mock_generate_documentation.assert_called_once_with(
        docs_dir="env_docs",
        sitemap_path="sitemap.xml",  # default unchanged
        skip_md_files=True,
        skip_llms_txt=True,
        skip_llms_full_txt=False,  # default unchanged
        llms_txt_name="env.txt",
        llms_full_txt_name="llms-full.txt",  # default unchanged
        model_name="gpt-4",
    )


def test_cli_overrides_environment(mock_generate_documentation):
    """Test that CLI arguments override environment variables."""
    env_vars = {
        "INPUT_DOCS_DIR": "env_docs",
        "INPUT_MODEL_NAME": "env-model",
    }

    test_args = [
        "script",
        "--docs-dir",
        "cli_docs",
        "--model-name",
        "cli-model",
    ]

    with patch.dict(os.environ, env_vars), patch("sys.argv", test_args):
        main()

    mock_generate_documentation.assert_called_once_with(
        docs_dir="cli_docs",  # CLI takes precedence
        sitemap_path="sitemap.xml",
        skip_md_files=False,
        skip_llms_txt=False,
        skip_llms_full_txt=False,
        llms_txt_name="llms.txt",
        llms_full_txt_name="llms-full.txt",
        model_name="cli-model",  # CLI takes precedence
    )
