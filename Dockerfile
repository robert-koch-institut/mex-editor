# syntax=docker/dockerfile:1@sha256:ecfaec9ed6d810b56388c508f4121597bfbba70d41a6dfeee4d8cad5f295fc32

FROM python:3.14@sha256:8edbf9e42c7fb168b9c523718ed907117e6d2e60f5889c0c499bbda3a787da53 AS builder

WORKDIR /build

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_INPUT=on
ENV PIP_PREFER_BINARY=on
ENV PIP_PROGRESS_BAR=off

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN uv export --no-dev --no-editable | uv pip install --system --no-deps -r -

RUN install-frontend
RUN MEX_EDITOR__CLIENT_DIR="/build/dist" MEX_EDITOR__BASE_HREF="/"        build-frontend
RUN MEX_EDITOR__CLIENT_DIR="/build/dist" MEX_EDITOR__BASE_HREF="/editor/" build-frontend

FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6

LABEL org.opencontainers.image.authors="mex@rki.de"
LABEL org.opencontainers.image.description="The editor enables anyone to create and edit entities in a simple and fast way."
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://github.com/robert-koch-institut/mex-editor"
LABEL org.opencontainers.image.vendor="robert-koch-institut"

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

ENV MEX_EDITOR__CLIENT_DIR="/app/dist"
ENV MEX_EDITOR__HOST="0.0.0.0"
ENV MEX_EDITOR__BASE_HREF="/"

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin/editor /usr/local/bin/editor
COPY --from=builder --chown=10001:10001 /build/dist /app/dist

USER 10001

EXPOSE 8000

ENTRYPOINT [ "editor" ]
