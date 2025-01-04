# llms-txt-actions

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/your-org/docs-actions)](https://github.com/your-org/docs-actions/releases)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/demodrive-ai/llms-txt-action/ci.yml?branch=main)](https://github.com/demodrive-ai/llms-txt-actions/actions)
[![License](https://img.shields.io/github/license/demodrive-ai/llms-txt-actions)](LICENSE)


### Make your documentation LLM friendly.

This Github action/CLI tool can automatically generate markdown (.md) files for each endpoint in your documentation as per the standard proposed by [answer.ai](https://www.answer.ai/), for more details read: https://llmstxt.org/.

![File Structure](docs/file_structure.png)



## Features

- 📄 **Content Processing**: Generate LLM-ready markdown (.md) files from popular document frameworks such as [Readthedocs](https://readthedocs.io/), [MKDocs](https://www.mkdocs.org/), [Sphinx](https://www.sphinx-doc.org/en/master/index.html#) and more.
- 🌈 **All Formats** : Can process HTML, PDF, Images, DOCX, PPTX, XLSX (thanks to [docling](https://github.com/DS4SD/docling)) and convert them to Markdown. (coming soon)
- 0️⃣ **Zero Config**: Works out of the box for most file based documentation framework.
- 💾 **Generate Summaries**: Using LLMs, we generate concise summary of each page.
- **BYO-Model**: Thanks to litellm, you can use upto 150 models.


## Quick Start

There are two ways to access this library.

1. Add this to your GitHub workflow:

```yaml

    steps:
      - name: Generate llms.txt
        uses: demodrive-ai/llms-txt-action@v0.1.0
        with:
          generate_md_files: true
          # any other inputs you would like to set.
```
OR

You can use it outside of Github Action.

```bash
# python 3.9 or above
pip install llms-txt-action

llms-txt --docs-dir site/
# The first run takes a while as it downloads models files from the intrnet.
```

## Input Parameters
| Parameter           | Required | Default    | Description                                  |
|---------------------|----------|------------|----------------------------------------------|
| `docs_dir`          | No       | `site/`    | Documentation output directory               |
| `skip_llms_txt`     | No       | `true`     | Skip llms.txt file generation.                   |
| `skip_llms_full_txt` | No  | `true`     | skip llms_full.txt file generation.              |
| `skip_md_files`     | No       | `true`     | Skip generation of markdown files                |
| `llms_txt_name`     | No       | `llms.txt` | Name of the llms.txt output file             |
| `llms_full_txt_name`| No       | `llms_full.txt` | Name of the llms_full.txt output file   |
| `sitemap_path`      | No       | `sitemap.xml` | Path relative to docs_dir to the sitemap.xml file [default: sitemap.xml] |
| `model_name`        | No       | `gpt-4o`    | Whether to push generated files to github artifacts |
| `model_max_tokens`  | No       | `2000`      | Limit the number of tokens to send per summary request |




## Secret Parameters
| Parameter           | Required | Default    | Description                                 |
|---------------------|----------|------------|----------------------------------------------|
| `MODEL_API_KEY`          | No       | None    | This key will be used to summarize pages for llms.txt               |




## Local Development

1. Clone and install:

   ```bash
   # clone the repo
   poetry install
   ```

1. Run the crawler:

   ```bash
   poetry run python -m "llms_txt_action.entrypoint" --docs-dir site/
   ```

## Examples

### ReadtheDocs

To integrate llms-txt-action with ReadtheDocs, you'll need to configure two files in your project:

1. `.readthedocs.yaml` - The main ReadtheDocs configuration file that defines the build environment and process
2. `docs/requirements.txt` - Python package dependencies needed for building your documentation

Here's how to set up both files:

```yaml
# .readthedocs.yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.12" # ^3.9 is supported.
  jobs:
    post_build:
      - llms-txt --docs-dir $READTHEDOCS_OUTPUT/html

mkdocs:
  configuration: mkdocs.yml

python:
  install:
  - requirements: docs/requirements.txt

```

```txt
# docs/requirements.txt
llms-txt-action==0.1.0
```

### MkDocs + Github Pages

MkDocs is a fast and simple static site generator that's geared towards building project documentation. Here's how to integrate llms-txt-action with MkDocs when deploying to GitHub Pages:

1. First, ensure you have a working MkDocs setup with your documentation source files.

2. Create or update your GitHub Actions workflow file (e.g., `.github/workflows/docs.yml`) with the following configuration:


```yaml
# github action - .github/workflows/docs.yml

      - name: Generate static files
        run : mkdocs build

      - name: Generate llms.txt, md files.
        uses: demodrive-ai/llms-txt-action@v0.1.0
        with:
          generate_md_files: true

      - name: Deploy to Github
        run : mkdocs gh-deploy --dirty
        # --dirty helps keep the generated .md and .txt files from getting deleted.
```

### Sphinx + Github Pages
Sphinx is a popular documentation generator for Python projects. Here's how to integrate llms-txt-action with Sphinx and GitHub Pages:

1. First, ensure you have a working Sphinx documentation setup with a `docs/` directory containing your source files and configuration.

2. Create or update your GitHub Actions workflow file (e.g., `.github/workflows/docs.yml`) with the following configuration:

```yaml
#...
#...
      - name: Build HTML
        uses: ammaraskar/sphinx-action@master
      - name: Generate llms.txt, md files.
        uses: demodrive-ai/llms-txt-action@v0.1.0
        with:
          name: docs-dir
          path: docs/build/html/
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: docs/build/html
#...
#...
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
