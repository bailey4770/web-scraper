FROM python:3.12-trixie
COPY --from=ghcr.io/astral-sh/uv:0.10.6 /uv /uvx /bin/

WORKDIR /app

ENV UV_NO_DEV=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --locked --no-install-project

# Copy the project into the image
COPY . /app

# Sync the project into a new environment, asserting the lockfile is up to date
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked 

ENTRYPOINT ["uv", "run", "scraper"]
