# syntax=docker/dockerfile:1
ARG PYTHON_VERSION={{ cookiecutter.python_version }}
FROM {{ cookiecutter.__docker_image }} AS base

# Install uv by copying its static binary from the official image [1].
# [1] https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Remove docker-clean so we can keep the apt cache in Docker build cache.
RUN rm /etc/apt/apt.conf.d/docker-clean

# Configure Python to print tracebacks on crash [1], and to not buffer stdout and stderr [2].
# [1] https://docs.python.org/3/using/cmdline.html#envvar-PYTHONFAULTHANDLER
# [2] https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1

# Configure uv: compile bytecode for faster startup, copy packages into the venv
# (required when mounting the cache), and never download a managed Python [1].
# [1] https://docs.astral.sh/uv/reference/environment/
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=never

# Install compilers that may be required for certain packages or platforms.
RUN --mount=type=cache,target=/var/cache/apt/ \
    --mount=type=cache,target=/var/lib/apt/ \
    apt-get update && \
    apt-get install --no-install-recommends --yes build-essential

# Create a non-root user and switch to it [1].
# [1] https://code.visualstudio.com/remote/advancedcontainers/add-nonroot-user
ARG UID=1000
ARG GID=$UID
RUN groupadd --gid $GID user && \
    useradd --create-home --gid $GID --uid $UID user --no-log-init && \
    chown user /opt/
USER user

# Create and activate a virtual environment.
ENV VIRTUAL_ENV=/opt/{{ cookiecutter.__project_name_kebab_case }}-env
ENV PATH=$VIRTUAL_ENV/bin:$PATH
ENV UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV
RUN uv venv $VIRTUAL_ENV

# Set the working directory.
WORKDIR /workspaces/{{ cookiecutter.__project_name_kebab_case }}/

# Install the run time Python dependencies in the virtual environment. The lock file is
# optional here (a freshly scaffolded project has none): uv resolves and writes uv.lock
# on the first build, which is then surfaced back to the workspace in the dev stage.
COPY --chown=user:user pyproject.toml uv.lock* /workspaces/{{ cookiecutter.__project_name_kebab_case }}/
RUN mkdir -p src/{{ cookiecutter.__project_name_snake_case }}/ && \
    touch src/{{ cookiecutter.__project_name_snake_case }}/__init__.py && touch README.md
RUN --mount=type=cache,uid=$UID,gid=$GID,target=/home/user/.cache/uv/ \
    uv sync --no-default-groups



FROM base AS dev

# Install development tools: curl, git, gpg, ssh, starship, sudo, vim, and zsh.
USER root
RUN --mount=type=cache,target=/var/cache/apt/ \
    --mount=type=cache,target=/var/lib/apt/ \
    apt-get update && \
    apt-get install --no-install-recommends --yes curl git gnupg ssh sudo vim zsh && \
    git config --system safe.directory '*' && \
    sh -c "$(curl -fsSL https://starship.rs/install.sh)" -- "--yes" && \
    usermod --shell /usr/bin/zsh user && \
    echo 'user ALL=(root) NOPASSWD:ALL' > /etc/sudoers.d/user && chmod 0440 /etc/sudoers.d/user
USER user

# Install the development Python dependencies in the virtual environment.
RUN --mount=type=cache,uid=$UID,gid=$GID,target=/home/user/.cache/uv/ \
    uv sync

# Persist output generated during docker build so that we can restore it in the dev container.
COPY --chown=user:user .pre-commit-config.yaml /workspaces/{{ cookiecutter.__project_name_kebab_case }}/
RUN mkdir -p /opt/build/uv/ && cp uv.lock /opt/build/uv/ && \
    git init && pre-commit install --install-hooks && \
    mkdir -p /opt/build/git/ && cp .git/hooks/commit-msg .git/hooks/pre-commit /opt/build/git/

# Configure the non-root user's shell.
ENV ANTIDOTE_VERSION=1.8.6
RUN git clone --branch v$ANTIDOTE_VERSION --depth=1 https://github.com/mattmc3/antidote.git ~/.antidote/ && \
    echo 'zsh-users/zsh-syntax-highlighting' >> ~/.zsh_plugins.txt && \
    echo 'zsh-users/zsh-autosuggestions' >> ~/.zsh_plugins.txt && \
    echo 'source ~/.antidote/antidote.zsh' >> ~/.zshrc && \
    echo 'antidote load' >> ~/.zshrc && \
    echo 'eval "$(starship init zsh)"' >> ~/.zshrc && \
    echo 'HISTFILE=~/.history/.zsh_history' >> ~/.zshrc && \
    echo 'HISTSIZE=1000' >> ~/.zshrc && \
    echo 'SAVEHIST=1000' >> ~/.zshrc && \
    echo 'setopt share_history' >> ~/.zshrc && \
    echo 'bindkey "^[[A" history-beginning-search-backward' >> ~/.zshrc && \
    echo 'bindkey "^[[B" history-beginning-search-forward' >> ~/.zshrc && \
    mkdir ~/.history/ && \
    zsh -c 'source ~/.zshrc'

FROM base AS app

# Copy the {{ cookiecutter.project_type }} source code to the working directory.
COPY --chown=user:user ./src ./src
COPY --chown=user:user ./pyproject.toml ./uv.lock ./

# Install the {{ cookiecutter.project_type }} itself into the virtual environment. A committed
# uv.lock is required to build this target so the runtime image is fully reproducible.
RUN --mount=type=cache,uid=$UID,gid=$GID,target=/home/user/.cache/uv/ \
    uv sync --no-default-groups --frozen
{%- if cookiecutter.with_fastapi_api|int %}

# Health check using stdlib only (no curl in slim images).
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Expose the app.
ENTRYPOINT ["/opt/{{ cookiecutter.__project_name_kebab_case }}-env/bin/poe"]
CMD ["api"]
{%- endif %}
