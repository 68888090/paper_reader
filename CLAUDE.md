# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install project in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .
```

## Architecture

- **src/claude_all/** - Main package code
- **tests/** - Test files
- **pyproject.toml** - Project configuration (dependencies, build system, linting, testing)

Uses setuptools for building. The project follows a standard Python package structure.
