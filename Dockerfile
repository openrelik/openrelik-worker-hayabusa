# Use the official Docker Hub Ubuntu base image
FROM ubuntu:24.04

# Prevent needing to configure debian packages, stopping the setup of
# the docker container.
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

# Install poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-poetry \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Configure poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set working directory
WORKDIR /openrelik

# Copy files needed to build
COPY . ./

# Install the worker and set environment to use the correct python interpreter.
RUN poetry install && rm -rf $POETRY_CACHE_DIR
ENV VIRTUAL_ENV=/app/.venv PATH="/openrelik/.venv/bin:$PATH"

# ----------------------------------------------------------------------
# Install Hayabusa
# ----------------------------------------------------------------------
# Define a build argument for the Hayabusa version (with a default)
ARG HAYABUSA_VERSION=2.17.0
ENV HAYABUSA_ZIP="hayabusa-${HAYABUSA_VERSION}-linux-intel.zip"

# Download the specified Hayabusa release using curl
RUN curl -L -o ${HAYABUSA_ZIP} https://github.com/Yamato-Security/hayabusa/releases/download/v${HAYABUSA_VERSION}/${HAYABUSA_ZIP}

# Unzip and clean up
RUN unzip ${HAYABUSA_ZIP} -d /hayabusa && rm ${HAYABUSA_ZIP}

# Rename the extracted directory for easier reference
RUN HAYABUSA_EXTRACTED_DIR="/hayabusa/hayabusa-${HAYABUSA_VERSION}-lin-x64-gnu" && \
    mv "${HAYABUSA_EXTRACTED_DIR}" /hayabusa/hayabusa

# Make Hayabusa executable
RUN chmod 755 /hayabusa/hayabusa

# Update Hayabusa rules
RUN /hayabusa/hayabusa update-rules
# ----------------------------------------------------------------------

# Default command if not run from docker-compose (and command being overidden)
CMD ["celery", "--app=openrelik_worker_hayabusa.tasks", "worker", "--task-events", "--concurrency=1", "--loglevel=INFO"]
