# syntax=docker/dockerfile:1

FROM python:3.11 AS base

LABEL org.opencontainers.image.authors="mex@rki.de"
LABEL org.opencontainers.image.description="Metadata editor web application."
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://github.com/robert-koch-institut/mex-editor"
LABEL org.opencontainers.image.vendor="robert-koch-institut"

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_INPUT=on
ENV PIP_PREFER_BINARY=on
ENV PIP_PROGRESS_BAR=off

ENV APP_NAME=mex
ENV FRONTEND_PORT=8030
ENV DEPLOY_URL=http://0.0.0.0:8030
ENV BACKEND_PORT=8031
ENV API_URL=http://0.0.0.0:8031
ENV TELEMETRY_ENABLED=False
ENV REFLEX_ENV_MODE=prod
ENV REFLEX_DIR=/app/reflex

ENV PATH="/app/.local/bin:$PATH"

RUN adduser \
--disabled-password \
--gecos "" \
--shell "/sbin/nologin" \
--home "/app" \
--uid "10001" \
mex

WORKDIR /app

COPY --chown=mex . .

USER mex

RUN --mount=type=cache,target=/app/.cache/pip pip install --no-deps --user --requirement locked-requirements.txt
RUN export-frontend

EXPOSE 8030
EXPOSE 8031

ENTRYPOINT [ "editor" ]
