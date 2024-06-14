# syntax=docker/dockerfile:1

FROM python:3.11 as base

LABEL org.opencontainers.image.authors="mex@rki.de"
LABEL org.opencontainers.image.description="Metadata editor web application."
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://github.com/robert-koch-institut/mex-editor"
LABEL org.opencontainers.image.vendor="robert-koch-institut"

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

ENV PIP_PROGRESS_BAR=off
ENV PIP_PREFER_BINARY=on
ENV PIP_DISABLE_PIP_VERSION_CHECK=on

ENV APP_NAME=mex
ENV FRONTEND_PORT=3000
ENV DEPLOY_URL=http://0.0.0.0:3000
ENV BACKEND_PORT=8000
ENV API_URL=http://0.0.0.0:8000
ENV TELEMETRY_ENABLED=False

WORKDIR /app

RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "10001" \
    mex

COPY . .

RUN --mount=type=cache,target=/root/.cache/pip pip install .

USER mex

EXPOSE 3000
EXPOSE 8000

ENTRYPOINT [ "editor" ]
