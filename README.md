# Docs to LLM Text

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/your-org/docs-actions)](https://github.com/your-org/docs-actions/releases)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/your-org/docs-actions/ci.yml?branch=main)](https://github.com/your-org/docs-actions/actions)
[![License](https://img.shields.io/github/license/your-org/docs-actions)](LICENSE)

Convert documentation websites into LLM-ready text files. Perfect for training or fine-tuning language models on your documentation.

## Features

- 🕷️ **Website Crawling**: Crawl documentation websites and save content in multiple formats
- 📄 **Content Processing**: Generate LLM-ready text files from crawled content
- 💾 **Multiple Output Formats**: Save content in HTML, Markdown, and metadata formats
- 🔄 **Automatic Retries**: Built-in polling and retry mechanism for large crawls
- 📦 **GitHub Action**: Easy integration into your workflows
- 🎨 **Rich CLI**: Beautiful command-line interface with progress tracking

## Quick Start

Add this to your GitHub workflow:

```yaml
name: Crawl Docs
on:
  schedule:
    - cron: "0 0 * * 0" # Weekly on Sundays
  workflow_dispatch: # Manual trigger

jobs:
  crawl:
    runs-on: ubuntu-latest
    steps:
      - name: Crawl Documentation
        uses: your-org/docs-actions@v1
        with:
          url: "https://docs.example.com"
          api_key: ${{ secrets.FIRECRAWL_API_KEY }}
          page_limit: 100

      - name: Process Output
        run: |
          echo "✨ Crawled content available in docs/crawled/"
          ls -la docs/crawled/
```

## Input Parameters

| Parameter       | Required | Default                | Description                               |
| --------------- | -------- | ---------------------- | ----------------------------------------- |
| `url`           | Yes      | -                      | URL of the documentation website to crawl |
| `api_key`       | Yes      | -                      | Firecrawl API key                         |
| `page_limit`    | No       | 100                    | Maximum number of pages to crawl          |
| `output_dir`    | No       | docs/crawled           | Directory to save crawled content         |
| `formats`       | No       | html,markdown,metadata | Output formats                            |
| `artifact_name` | No       | crawled-docs           | Name of the uploaded artifact             |

## Output Structure

The action generates the following files for each crawled page:

```
docs/crawled/YYYYMMDD_HHMMSS/
├── crawl_metadata.json     # Crawl statistics and metadata
├── llms-full.txt          # Combined markdown content for LLM processing
├── page_0_html.html       # Raw HTML content
├── page_0_md.md          # Markdown content
└── page_0_meta.json      # Page metadata
```

## Local Development

1. Clone and install:

   ```bash
   git clone https://github.com/your-org/docs-actions.git
   cd docs-actions
   poetry install
   ```

2. Set your API key:

   ```bash
   export FIRECRAWL_API_KEY=your-key-here
   ```

3. Run the crawler:
   ```bash
   poetry run python src/docs_actions/crawl.py \
     --url "https://docs.example.com" \
     --limit 100 \
     --output docs/crawled
   ```

## Examples

### Basic Usage

```yaml
- uses: your-org/docs-actions@v1
  with:
    url: "https://docs.example.com"
    api_key: ${{ secrets.FIRECRAWL_API_KEY }}
```

### Full Configuration

```yaml
- uses: your-org/docs-actions@v1
  with:
    url: "https://docs.example.com"
    api_key: ${{ secrets.FIRECRAWL_API_KEY }}
    page_limit: 500
    output_dir: "custom/output/dir"
    formats: "html,markdown"
    artifact_name: "my-docs"
```

### Multiple Sites

```yaml
jobs:
  crawl-docs:
    strategy:
      matrix:
        site:
          - "https://docs.example.com"
          - "https://api.example.com"
          - "https://help.example.com"
    runs-on: ubuntu-latest
    steps:
      - uses: your-org/docs-actions@v1
        with:
          url: ${{ matrix.site }}
          api_key: ${{ secrets.FIRECRAWL_API_KEY }}
          artifact_name: docs-${{ github.sha }}-${{ strategy.job-index }}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
