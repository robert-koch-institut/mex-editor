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

ENV REFLEX_DIR="/app/reflex"
ENV REFLEX_ENV_MODE="prod"
ENV REFLEX_SKIP_COMPILE="True"
ENV REFLEX_WEB_WORKDIR="web"

RUN adduser \
--disabled-password \
--gecos "" \
--shell "/sbin/nologin" \
--home "/app" \
--uid "10001" \
mex

WORKDIR /app

COPY . .

RUN --mount=type=cache,target=/root/.cache pip install --no-deps --requirement locked-requirements.txt
RUN --mount=type=cache,target=/root/.npm reflex init && reflex export --frontend-only --no-zip
RUN chown -R 10001:10001 /app

USER mex

EXPOSE 8030
EXPOSE 8031

ENTRYPOINT [ "editor-frontend" ]
