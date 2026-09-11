# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

Nothing here has been released yet. Entries are split into the current change
set — itself grouped by whether it came from upstream or from us — and the
Baseline work that was already sitting unreleased before it.

### Current — upstream sync

Taken from [superlinear-ai/substrate](https://github.com/superlinear-ai/substrate),
catching up from our last merge base (substrate#240) to upstream v2.1.0.

#### Changed (breaking)

- **Template engine is now [Copier](https://copier.readthedocs.io/) instead of
  Cookiecutter** (substrate#320). Scaffold with
  `uvx copier copy gh:Baseline-quebec/baseline-app-cookiecutter <dir>` and
  update with `uvx copier update`. Template sources moved to `template/` with a
  `.jinja` suffix; `cookiecutter.json` became `copier.yml`; the generation
  hooks became per-question validators and conditional file paths. Projects
  generated with Cookiecutter need a one-time migration from `.cruft.json` to
  `.copier-answers.yml` — see the README.
- Copier resolves a template to its **newest git tag**, so template releases
  must now be tagged (`cz bump`) to reach generated projects.
- **Build backend is now `uv_build` instead of hatchling** (substrate#324).
- Commitizen bumps through the `uv` version provider (substrate#293), keeping
  `uv.lock` in step with the version.
- The ruff formatter formats docstring code and ignores magic trailing commas;
  the FastAPI and BDD stubs are reflowed to match.
- VS Code fix-on-save is scoped to `[python]` and to ruff's own code actions.
- Generated CI checks PR titles with `uvx --from=commitizen cz check`, pins
  `@devcontainers/cli`, and uses current action majors.

#### Added

- Well-known `[project.urls]` labels (homepage, source, changelog,
  releasenotes, issues)
- `check-illegal-windows-names` pre-commit hook (substrate#284)

#### Fixed

- The API server never received SIGTERM: the container entrypoint ran the
  server behind a shell, so `docker stop` skipped graceful shutdown and waited
  out its timeout on every deploy (substrate#343). Upstream's version of this
  fix does not work as written — its control expression matches no case and the
  task silently runs nothing — so ours uses `bool(${dev})`.
- `*.egg-info/` was never git-ignored, so editable install output landed in the
  first commit of every generated project (substrate#273)
- A local `.venv/` was copied into the Docker build context

#### Not adopted

- **ty** (substrate#321): pre-1.0 with no plugin system, and the template
  depends on the `pydantic.mypy` plugin. We stay on mypy.
- Upstream's ruff ruleset, `testpaths = ["src", "tests"]`, their Dockerfile and
  docker-compose rewrites, and dropping the `package` project type or the
  GitLab CI provider.

### Current — Baseline

Our own decisions in this change set, which in places deliberately diverge from
upstream.

#### Changed (breaking)

- CI runs on uv: unit tests install from a lock file on Python 3.12, 3.13 and
  3.14, with a lint job so the ruff config is enforced rather than advisory.
  Integration scaffolds and runs a project on 3.12 (full), 3.13 (minimal) and
  3.14 (full).
- `astral-sh/setup-uv` is pinned to an exact version: it publishes no floating
  major tag past v7 despite releases well beyond it, so `@v10` does not resolve
  and fails every job during setup.

#### Removed

- **Documentation generation.** No `mkdocs.yml`, no `mkdocs-material`
  dependency, no `poe docs` task and no GitHub Pages workflow. Architecture
  decision records stay as plain markdown under `docs/decisions/`; only the
  site generator is gone. Upstream keeps MkDocs, so this is a deliberate
  divergence. MkDocs was added earlier in this same unreleased window and so
  never shipped.
- This repository's AGPL-3.0 `LICENSE`, inherited from substrate before it
  relicensed to MIT.
- The generated `LICENSE` file, matching upstream. The `license` answer is
  still recorded as SPDX metadata in the generated `pyproject.toml`.

#### Added

- A `pyproject.toml` and `uv.lock` for this repository itself, so its test
  dependencies are declared and ruff is configured against its own test suite.
  `[tool.uv] package = false` — this is a template, not an installable package.
  Commitizen is configured here so `cz bump` tags releases, which is what
  publishes a template change to generated projects; it does not touch this
  changelog, which is maintained by hand.

#### Fixed

- Script injection in the PR title check, in this repository's workflow and the
  generated one: the attacker-controlled title was interpolated straight into a
  shell command. It now goes through an environment variable.
- `TC003` is ignored in strict mode. On Python 3.14 (PEP 649) ruff wants the
  stdlib typing import hoisted into a type-checking block and the quotes
  removed, which raises `NameError` on 3.12 and 3.13; one template source
  cannot satisfy both.
- Broken relative link to `decisions/` in the generated `docs/index.md`, before
  that file was removed with the rest of the docs stack.

### Earlier, still unreleased

Baseline work that predates the change set above. A few entries are superseded
by it — notably MkDocs, the Cruft link check, and the CI matrix.

#### Added

- `CLAUDE.md` template for AI-assisted development in generated projects
- `pull_request_template.md` for the cookiecutter repo itself
- `CODEOWNERS` file (@davebulaval, @dpothier)
- Fast CI workflow (`ci.yml`) — unit tests on Python 3.12 + 3.13 (~20s)
- PR title check workflow (`pr.yml`) — conventional commits validation
- Integration test matrix — full (FastAPI + Typer) and minimal (bare) variants
- Cruft link verification step in integration tests
- codespell linter in pre-commit and pyproject.toml
- MkDocs Material for documentation (replaces pdoc)
- PR title check workflow for generated projects (`pr.yml`)
- `detect-secrets` (Yelp) pre-commit hook to block accidental credential commits
- `actionlint` pre-commit hook for GitHub Actions validation
- `ruff-check` and `ruff-format` pre-commit hooks for template code
- `pre-commit-hooks` (check-yaml, check-toml, end-of-file-fixer, trailing-whitespace)
- 71 unit tests for template generation (up from 0)

#### Changed

- Conditionalized generated README sections (API, CLI, Docker) with Jinja
- Rewrote root README with CI badges, project structure, and developer guide
- Rewrote generated README: concise and dynamic
- Modernized integration workflow: checkout v6, pip cache, renamed to "Integration"
- Fixed generated CONTRIBUTING.md typos and added codespell to tools list
- Fixed `.env.sample` reference to `.env.example` in generated README

#### Fixed

- ruff lint errors in generated code (FURB171, PLC0415, PLR2004, PLR6201, B007, PERF102)
- codespell false positives (Jupyter) and real typos (developpement, developpers, formater)
- Jinja whitespace in cli.py imports causing ruff format failure
- Unused `import sys` and stale noqa comments (S310, BLE001) in cli.py
- Coverage failure in minimal config (added settings test)

---

## Sprint 2 — Cookiecutter Enhancements

### Added

- pydantic-settings integration (replaces python-decouple) with `.env.example`
- Pydantic models (`models.py`) and service layer (`services.py`) stubs
- Rich API stubs: health endpoint, CRUD items, exception handlers, request logging middleware
- Rich CLI stubs: `info` command with Rich table, `greet` command with `Annotated`
- `.editorconfig` for cross-IDE consistency
- `.vscode/launch.json` with FastAPI, pytest, and current-file debug configs
- `CHANGELOG.md` for generated projects (Keep a Changelog format)
- `pre_gen_project.py` hook for input validation
- Sentry SDK integration (`with_sentry` parameter)
- Multi-Python CI matrix (tests on selected version + 3.13)
- Docker `HEALTHCHECK` instruction (conditional on FastAPI)
- pytest-asyncio support (conditional on FastAPI)

### Changed

- Replaced python-decouple with pydantic-settings
- Rewrote `api.py` with dependency injection, structured error handling, and logging
- Rewrote `cli.py` with `@app.callback()` and `Annotated` pattern
- Rewrote BDD test stubs for new API and CLI
- Renamed `.env_sample` to `.env.example`
- Removed Teamwork integration (workflow + PR template link)

### Fixed

- 5 P0 bugs that broke template generation
- pytest-bdd feature file paths
- pre-commit hook compatibility (pygrep-hooks tag, `--pytest-test-first`)
- ruff preview mode compliance (DOC201, DOC501, FAST001, PLR6301, etc.)
- mypy strict mode compliance
- typeguard conflict with typer.Context
