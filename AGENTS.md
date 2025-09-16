# Repository Guidelines

## Project Structure & Modules
- src: Python package in `src/garmin_daily` (CLI entry in `main.py`).
- tests: Pytest suite in `tests/` with `test_*.py` files and fixtures.
- docs: MkDocs config in `docs/` and scripts under `scripts/`.
- config: Lint/type/test config in `.pre-commit-config.yaml`, `.flake8`, `.pylintrc`, `.coveragerc`, `pytest.ini`.
- packaging: `setup.py`, `setup.cfg`, `MANIFEST.in`; console script `garmin-daily` installed via entry_points.

## Dev Setup, Build & Run
- Environment: `. ./activate.sh` (creates `.venv`, installs dev deps, editable install).
- Lint/format/type-check: `pre-commit install && pre-commit run -a`.
- Tests: `pytest` or `pytest --cov=garmin_daily --cov-report=term-missing`.
- Docs (serve): `make docs` or API docs: `make docs-src`.
- Version bump: `make ver-bug | ver-feature | ver-release`.
- Package build/upload: `scripts/build.sh` then `scripts/upload.sh`.
- Run CLI locally: `garmin-daily --version` or `python -m garmin_daily.main --help`.

## Coding Style & Naming
- Language: Python ≥ 3.9; 4-space indents; UTF-8; Unix newlines.
- Style: Ruff + Flake8 (line length ~100). Import order enforced by Ruff.
- Types: Prefer type hints; keep mypy happy (`pre-commit` runs mypy on `src/`).
- Names: `snake_case` for functions/vars/modules, `PascalCase` for classes, constants UPPER_CASE.
- Docstrings: Brief, with runnable examples where practical (doctest enabled).

## Testing Guidelines
- Framework: Pytest with doctest (`pytest.ini` adds `--doctest-modules`).
- Location/naming: Place tests in `tests/` as `test_*.py`; mirror module names when possible.
- Coverage: Use `pytest --cov=garmin_daily`; configuration omits tests and generated files.
- CLI tests: Use `click.testing.CliRunner` (see `tests/test_main.py`) and mock external services.

## Commit & PR Guidelines
- Commits: Imperative mood; small, focused changes. Link issues (e.g., `https://github.com/.../issues/123`). Version tags are created via `make ver-*`.
- Before PR: Ensure `pre-commit run -a` and `pytest` pass; update docs if CLI/behavior changes.
- PR description: What/why, linked issue(s), testing notes; include sample CLI output when relevant.

## Security & Configuration
- Do not commit credentials or tokens. Follow the User Manual “Credentials” section for Google/Garmin setup.
- Store secrets outside the repo (env vars, local config). Add any new secrets to CI only via encrypted settings.
