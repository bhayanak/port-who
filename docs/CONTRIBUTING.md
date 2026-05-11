# Contributing to Port Who

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone the repo
git clone https://github.com/port-who/port-who.git
cd port-who

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run full test suite with coverage
pytest --cov=port_who --cov-report=term-missing

# Run a specific test file
pytest tests/test_killer.py -v
```

## Code Quality

```bash
# Lint
ruff check src/ tests/

# Format check
ruff format --check src/ tests/

# Auto-fix
ruff check --fix src/ tests/
ruff format src/ tests/
```

## Pull Request Process

1. Fork the repository and create a feature branch from `main`
2. Write tests for your changes
3. Ensure all tests pass and coverage meets the threshold
4. Ensure `ruff check` and `ruff format --check` pass
5. Open a pull request with a clear description

## Reporting Issues

- Use [GitHub Issues](https://github.com/port-who/port-who/issues)
- Include your OS, Python version, and steps to reproduce
