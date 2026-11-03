# syntax=docker/dockerfile:1
# AESA tooling image — Python 3.15.2 slim (Debian trixie) + uv, locked deps.
# Base and uv pins use tag@digest so Dependabot can bump both.

FROM python:3.15.2-slim-trixie@sha256:8c13a3f37a6a5b71498228e902c4b9f51c1f7900d49fabf71f9a650c6120e0d0

# Official distroless uv binary image (pin version@digest).
COPY --from=ghcr.io/astral-sh/uv:0.13.7@sha256:96f40d3904aad8d0bd010539001d36c8e2188b981e1334471a90c4a1d93bb490 \
    /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0 \
    PATH="/app/tools/.venv/bin:$PATH"

WORKDIR /app

# Dependency layer: install locked runtime deps without the project (better cache).
# Production images exclude PEP 735 dev groups (--no-dev); do not copy a host .venv.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=tools/uv.lock,target=tools/uv.lock \
    --mount=type=bind,source=tools/pyproject.toml,target=tools/pyproject.toml \
    uv sync --locked --no-dev --no-install-project --directory tools

# Full kit (procedure, schemas, modules, …) + project sources.
COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --directory tools

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin aesa \
    && chown -R aesa:aesa /app
USER aesa

WORKDIR /work
ENTRYPOINT ["aesa"]
CMD ["--help"]
