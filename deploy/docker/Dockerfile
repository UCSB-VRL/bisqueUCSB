ARG BISQUE_ENV_IMAGE=bisque:env
FROM ${BISQUE_ENV_IMAGE}

# for licensing reasons do not build image with bioformats
ARG BISQUE_INSTALL_BIOFORMATS=0

WORKDIR /app

ENV BISQUE_APP_DIR=/app
ENV BISQUE_RUNTIME_DIR=/app/.bisque
ENV BISQUE_PUBLIC_DIR=/app/public
ENV HOME=/app/.cache/container-home
ENV VENV=/.venv
ENV UV_PROJECT_ENVIRONMENT=/.venv
ENV PYTHONNOUSERSITE=1
ENV BISQUE_AUTO_SYNC=0
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN mkdir -p /usr/bin "$HOME" && \
    ln -sf /bin/env /usr/bin/env

COPY scripts/container-build-step.sh scripts/install-converters.sh scripts/install-bioformats.sh /app/scripts/

RUN /app/scripts/container-build-step.sh install-converters "$BISQUE_INSTALL_BIOFORMATS"

COPY pyproject.toml uv.lock /app/

RUN /app/scripts/container-build-step.sh sync-deps

COPY . /app

RUN /app/scripts/container-build-step.sh install-app

ENV PATH="${VENV}/bin:${PATH}"

EXPOSE 8080

CMD ["bash", "/app/scripts/start-bisque-container.sh"]
