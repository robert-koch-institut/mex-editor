# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

FROM python:3.14@sha256:d18055009f327b22993de14458aa5a6bac032cdf459ea2a2e9bbdc3d3d49e4fb AS builder

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

FROM python:3.14-slim@sha256:9aaa474097d094040649f2162a627c0049b408f52138d980916788d80f04802f

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
