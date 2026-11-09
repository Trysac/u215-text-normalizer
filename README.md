# text-normalizer

[![PyPI version](https://img.shields.io/pypi/v/trysac-text-normalizer)](https://pypi.org/project/trysac-text-normalizer/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-text-normalizer)](LICENSE)
[![CI](https://github.com/Trysac/u215-text-normalizer/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u215-text-normalizer/actions/workflows/ci.yml)

Normalize text for indexing with an explicit, ordered rule set: zero-width removal, control characters, Unicode NFKC, curly quotes, dashes and whitespace, idempotent

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-text-normalizer
# or
uv add trysac-text-normalizer
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import text_normalizer

# normalize() trims surrounding whitespace and lower-cases the text.
print(text_normalizer.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    text_normalizer.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
