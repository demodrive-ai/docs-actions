FROM python:3.12-slim-bookworm

WORKDIR /app

# Install uv by copying from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the entire project
COPY . .

# Install the package and its dependencies
RUN uv pip install . --system

CMD ["python", "-m", "llms_txt_action.entrypoint"]
