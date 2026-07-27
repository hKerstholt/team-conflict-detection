# Start from a base image with uv and python 3.13
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# This image requires a valid OpenAI API key to run, which
# Docker Compose reads from the .env file or an environment
# variable with this name
ENV OPENAPI_API_KEY=""

# Copy only the uv configuration containing the list of dependencies
COPY ./pyproject.toml /src/pyproject.toml

# Commands inside the container will be run here
WORKDIR /src

# Install dependencies at build time
RUN uv sync

# Copy all files except those listed in .dockerignore
# Doing this after `uv sync`
COPY . /src/

# Make the application accessible on http://localhost:8501
EXPOSE 8501

# Run streamlit with uv by default, sync dependencies
CMD ["uv", "run", "streamlit", "run", "chat.py"]
