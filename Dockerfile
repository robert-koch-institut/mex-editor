# syntax=docker/dockerfile:1

FROM python:3.11 AS base

LABEL org.opencontainers.image.authors="mex@rki.de"
LABEL org.opencontainers.image.description="Metadata editor web application."
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://github.com/robert-koch-institut/mex-editor"
LABEL org.opencontainers.image.vendor="robert-koch-institut"

ENV PATH="$HOME/.local/bin:$PATH"

ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1
ENV PYTHONPATH="$HOME/.local/lib/python3.11/site-packages"

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_INPUT=on
ENV PIP_PREFER_BINARY=on
ENV PIP_PROGRESS_BAR=off

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

RUN --mount=type=cache,mode=0755,uid=10001,gid=10001,target=/app/.cache pip install --no-deps --user --requirement locked-requirements.txt
RUN --mount=type=cache,mode=0755,uid=10001,gid=10001,target=/app/.npm python -m reflex init && python -m reflex export --frontend-only --no-zip

EXPOSE 8030
EXPOSE 8031

ENTRYPOINT [ "editor" ]
