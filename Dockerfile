ARG PYTHON_BASE_IMAGE=python:3.12-slim

# `python-base` sets up all our shared environment variables
FROM ${PYTHON_BASE_IMAGE} AS python-base

# python
ENV PYTHONUNBUFFERED=1 \
  # prevents python creating .pyc files
  PYTHONDONTWRITEBYTECODE=1 \
  \
  # pip
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  \
  # poetry
  # https://python-poetry.org/docs/configuration/#using-environment-variables
  POETRY_VERSION=1.8.3 \
  # make poetry install to this location
  POETRY_HOME="/opt/poetry" \
  # make poetry create the virtual environment in the project's root
  # it gets named `.venv`
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  # do not ask any interactive question
  POETRY_NO_INTERACTION=1 \
  \
  # paths
  # this is where our requirements + virtual environment will live
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv"
ARG LOG_FILE_DIRECTORY="${PYSETUP_PATH}/logs"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# APT
ENV DEBIAN_FRONTEND=noninteractive

# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base AS builder-base
RUN apt update \
  && apt install --no-install-recommends -y \
  # deps for installing poetry
  curl \
  # deps for building python deps
  build-essential \
  && apt clean \
  && apt autopurge -y \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# setup user and folder for Poetry
RUN useradd --create-home appuser
RUN install -d -m 0755 -o appuser -g appuser $POETRY_HOME
USER appuser

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

# copy project requirement files here to ensure they don't change
WORKDIR $PYSETUP_PATH

FROM builder-base AS dev

USER root

# setup shell completion for poetry
RUN case "$0" in \
  *bash*) echo "setup Poetry shell completion for bash" && poetry completions bash > ${XDG_DATA_HOME:-~/.local/share}/bash-completion/completions/poetry ;; \
  *zsh*) echo "setup Poetry shell completion for zsh" && poetry completions zsh > "${fpath[1]}/_poetry" ;; \
  *fish*) echo "setup Poetry shell completion for fish" && poetry completions fish > ~/.config/fish/completions/poetry.fish ;; \
  *) echo "Poetry completions are not supported in your shell" ;; \
  esac

FROM builder-base AS prod_prepare

# plugin for exporting to requirements.txt
RUN poetry self add poetry-plugin-export@1.8.0

COPY ./pyproject.toml ./poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt --without dev

FROM python-base AS prod

# project deps
WORKDIR $PYSETUP_PATH
COPY --from=prod_prepare $PYSETUP_PATH/requirements.txt ./
RUN pip3 install --no-input --require-hashes --compile --user -r requirements.txt

# environment variables
COPY .env ./

# log file directory
RUN mkdir -p $LOG_FILE_DIRECTORY
RUN bash -c 'sed -i "s/^PT_FINAL_LOGFILE_PREFIX.*/PT_FINAL_LOGFILE_PREFIX=${LOG_FILE_DIRECTORY//\//\\/}\/log/g" .env'

# project files
COPY src src

CMD ["python3", "-m", "src.main"]
