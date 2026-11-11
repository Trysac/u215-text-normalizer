# text-normalizer

Normalize text for indexing with an explicit, ordered rule set.

## Installation

```bash
pip install trysac-text-normalizer
```

## Usage

```python
from text_normalizer import normalize, Options, explain

normalize("\ufeff\u201cHello\u201d\u00a0world \u2014 it\u2019s \ufb01ne")
# '"Hello" world - it\'s fine'

report = explain("\u201ca\u201d")
print(report.changed)  # ('quotes',)
```

## CLI

```bash
echo '\u201cHello\u201d' | text-normalizer --no-quotes
```

## Rules

Applied in this order:

1. **zero_width**: Remove U+200B, U+2060, U+FEFF, U+00AD (keep ZWJ/ZWNJ).
2. **controls**: Convert CRLF/CR to LF; remove C0/C1 controls except tab and LF.
3. **unicode**: Apply Unicode normalization (default NFKC; use `--form NFC` or `none`).
4. **quotes**: Curly quotes → straight quotes (guillemets kept).
5. **dashes**: Various dashes (including U+2212) → hyphen-minus.
6. **whitespace**: Replace non‑LF whitespace with space, collapse spaces, strip line ends,
   collapse 3+ LFs to two, strip overall.

## API

- `Options` (frozen dataclass): configure rules and `max_chars`.
- `normalize(text, options=Options()) -> str`
- `explain(text, options=Options()) -> Report` (contains `text` and `changed` tuple)
- `NormalizerError` with `code` (`invalid_option`, `input_too_large`, `invalid_input`)

## Development

See `CONTRIBUTING.md` for details.
