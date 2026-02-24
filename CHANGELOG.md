# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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

### Changed

- Conditionalized generated README sections (API, CLI, Docker) with Jinja
- Rewrote root README with CI badges, project structure, and developer guide
- Rewrote generated README: concise, dynamic, references MkDocs
- Modernized integration workflow: checkout v6, pip cache, renamed to "Integration"
- Fixed generated CONTRIBUTING.md typos and added codespell to tools list
- Fixed `.env.sample` reference to `.env.example` in generated README

### Fixed

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
