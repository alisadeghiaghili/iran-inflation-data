# Contributing to iran-inflation-data

Thank you for your interest in contributing! Here's how you can help:

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/iran-inflation-data.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Make your changes
5. Commit: `git commit -m "Add your feature"`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e ".[all,dev]"

# Run tests
pytest

# Format code
black src/ main.py

# Lint
flake8 src/ main.py
```

## Adding a New Data Source

1. Create a new fetcher in `src/fetchers/`
2. Follow the pattern in `world_bank.py`
3. Return a pandas DataFrame with columns: `date`, `year`, `month`, `value`, `source`
4. Add the fetcher to `src/fetchers/__init__.py`
5. Update `main.py` to include the new source

## Code Style

- Use Black for formatting (line length: 100)
- Follow PEP 8 guidelines
- Add type hints where possible
- Write docstrings for public functions

## Reporting Issues

- Use the GitHub issue tracker
- Include steps to reproduce
- Include Python version and OS
- Include error messages if applicable

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
