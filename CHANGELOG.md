# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
