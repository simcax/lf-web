# Use Chainguard's Python image
FROM python:3.13.2-slim AS builder

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV VIRTUAL_ENV=/app/.venv
# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY pyproject.toml .
COPY uv.lock .

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY README.md .

# Install the dependencies using uv
RUN uv venv
ENV PATH="/app/.venv/bin:$PATH"
RUN echo $PATH
RUN CC=gcc uv sync --frozen --no-dev

#FROM cgr.dev/chainguard/python:latest-dev
FROM python:3.13.2-slim
# Set the working directory
WORKDIR /app

# Copy the application code
COPY ./lfweb ./lfweb
COPY ./*.md ./

# Copy the dependencies from the builder image
COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"
# Copy the rest of the application code
RUN ls -la /app
RUN ls -la /app/.venv/bin
RUN python --version

# Expose the port the app runs on
EXPOSE 8000

# Set the FLASK_APP environment variable
ENV FLASK_APP=lfweb

# Command to run the application using Gunicorn
ENTRYPOINT ["/app/.venv/bin/gunicorn", "-b", "0.0.0.0:8000", "lfweb:create_app()"]
