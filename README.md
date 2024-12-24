# LLM-TXT-ACTION

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/your-org/docs-actions)](https://github.com/your-org/docs-actions/releases)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/your-org/docs-actions/ci.yml?branch=main)](https://github.com/your-org/docs-actions/actions)
[![License](https://img.shields.io/github/license/your-org/docs-actions)](LICENSE)

Convert documentation websites into LLM-ready text files. Perfect for training or fine-tuning language models on your documentation.
For more details read: https://llmstxt.org/

## Features

- 📄 **Content Processing**: Generate LLM-ready text files from popular document frameworks such as [MKDocs](https://www.mkdocs.org/), [Sphinx](https://www.sphinx-doc.org/en/master/index.html#) and more.
- 💾 **Multiple Output Formats**: Save content in HTML, Markdown, and metadata formats


## Quick Start

Add this to your GitHub workflow:

```yaml
    steps:
      - name: Generate llms.txt
        uses: demodrive-ai/llm-txt-action@v0.1.0
        with:
          generate_md_files: true
          # any other inputs you would like to set.
```

## Input Parameters
| Parameter           | Required | Default    | Description                                 |
|---------------------|----------|------------|----------------------------------------------|
| `docs_dir`          | No       | `site/`    | Documentation output directory               |
| `generate_llms_txt` | No       | `true`     | Whether to generate LLMS.txt file            |
| `generate_llms_full_txt` | No  | `true`     | Whether to generate llms_full.txt file       |
| `generate_md_files` | No       | `true`     | Generate md files for each html file         |
| `llms_txt_name`     | No       | `llms.txt` | Name of the llms.txt output file             |
| `llms_full_txt_name`| No       | `llms_full.txt` | Name of the llms_full.txt output file   |
| `poetry_version`    | No       | `latest`   | Poetry version to use (or 'latest')          |
| `push_to_git`       | No       | `false`    | Whether to push generated files to git       |
| `push_to_artifacts` | No       | `false`    | Whether to push generated files to artifacts |




## Local Development

1. Clone and install:

   ```bash
   # clone the repo
   poetry install
   ```

1. Run the crawler:

   ```bash
   poetry run python src/llms_txt_action/main.py --docs-dir site/
   ```

## Examples

1. Deploy MkDocs website to Github Pages.

```yaml
      - name: Generate static files
        run : mkdocs build

      - name: Generate llms.txt, md files.
        uses: demodrive-ai/llm-txt-action@v0.1.0
        with:
          generate_md_files: true

      - name: Deploy to Github
        run : mkdocs gh-deploy --dirty
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
