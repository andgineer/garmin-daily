# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Environment Setup
```bash
. ./activate.sh  # Creates/activates venv and installs package in editable mode
```

### Testing
```bash
pytest                    # Run all tests with doctest modules
pytest tests/test_*.py    # Run specific test file
```

### Code Quality
```bash
pre-commit run --all-files  # Run all linting and formatting checks
ruff --fix                  # Run ruff linter with auto-fix
ruff-format                 # Format code with ruff
mypy src/                   # Type checking (excludes tests)
```

### Build and Release
```bash
make help                   # Show all available make targets
make version               # Show current version
make ver-bug/ver-feature/ver-release  # Bump version
make reqs                  # Upgrade requirements and pre-commit
python setup.py sdist bdist_wheel  # Build distribution packages
```

### Documentation
```bash
make docs                  # Build and serve user documentation
make docs-src              # Build and serve API documentation from docstrings
```

## Architecture

This is a Python CLI tool that aggregates fitness data from Garmin Connect and exports it to Google Sheets.

### Core Components

- **`main.py`**: CLI entry point using rich-click, handles command-line arguments and orchestrates the data flow
- **`garmin_aggregations.py`**: Core `GarminDaily` class that connects to Garmin Connect API and aggregates daily fitness data (steps, activities, sleep)
- **`google_sheet.py`**: Google Sheets integration, handles authentication and data export with batch processing
- **`mappers.py`**: Data transformation classes (`ActivityMapper`, `LocationMapper`) for mapping Garmin activities to sheet formats
- **`columns_mapper.py`**: Maps between Garmin data fields and Google Sheet columns

### Data Flow
1. CLI parses arguments and detects date ranges to process
2. `GarminDaily` authenticates with Garmin Connect and fetches daily aggregated data
3. Mappers transform raw Garmin data to match Google Sheet structure
4. `google_sheet.py` batch-uploads data to Google Sheets with API rate limiting

### Key Features
- Automatic gym day detection based on weekday patterns
- Activity location mapping and sport type normalization
- Batch processing with API delays to prevent rate limiting
- Comprehensive error handling for authentication and API failures

### Configuration
- Package uses setuptools with src-layout (`src/garmin_daily/`)
- Entry point: `garmin-daily` command
- Python 3.9+ required (uses `Annotated` type hints)
- Uses ruff for linting/formatting with strict rules, mypy for type checking
- Pre-commit hooks enforce code quality standards
