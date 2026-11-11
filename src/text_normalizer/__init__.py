"""Normalize text for indexing with an explicit, ordered rule set."""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import Final, Literal

__all__ = ["NormalizerError", "Options", "Report", "explain", "normalize"]

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Character sets and translation tables (computed once).
_ZERO_WIDTH_CHARS: Final = {"\u200b", "\u2060", "\ufeff", "\u00ad"}
_ZERO_WIDTH_TRANS = str.maketrans({ord(c): None for c in _ZERO_WIDTH_CHARS})

_APOSTROPHE_SRC: Final = ("\u2018", "\u2019", "\u201a", "\u201b")
_DOUBLE_QUOTE_SRC: Final = ("\u201c", "\u201d", "\u201e", "\u201f")
_QUOTE_TRANS = str.maketrans(
    {ord(c): "'" for c in _APOSTROPHE_SRC} | {ord(c): '"' for c in _DOUBLE_QUOTE_SRC}
)

_DASH_SRC: Final = tuple(chr(c) for c in (*range(0x2010, 0x2016), 0x2212))
_DASH_TRANS = str.maketrans({ord(c): "-" for c in _DASH_SRC})

# C0 and C1 control characters to remove (keep tab and LF).
_CONTROL_REMOVAL: dict[int, None] = {}
for _code in range(0x00, 0x20):
    if _code not in (0x09, 0x0A):
        _CONTROL_REMOVAL[_code] = None
for _code in range(0x80, 0xA0):
    _CONTROL_REMOVAL[_code] = None
_CONTROL_TRANS = str.maketrans(_CONTROL_REMOVAL)


@dataclass(frozen=True)
class Options:
    """Configuration for normalization rules.

    Attributes:
        form: Unicode normalization form ('NFC', 'NFKC', or 'none').
        quotes: Replace curly quotes with straight quotes.
        dashes: Replace various dashes with hyphen-minus.
        whitespace: Normalize whitespace.
        zero_width: Remove zero-width characters (except ZWJ/ZWNJ).
        max_chars: Maximum input length accepted (in characters).
    """

    form: Literal["NFC", "NFKC", "none"] = "NFKC"
    quotes: bool = True
    dashes: bool = True
    whitespace: bool = True
    zero_width: bool = True
    max_chars: int = 10_000_000

    def __post_init__(self) -> None:
        if self.form not in ("NFC", "NFKC", "none"):
            raise NormalizerError("invalid_option")
        if not isinstance(self.max_chars, int) or self.max_chars <= 0:
            raise NormalizerError("invalid_option")


class NormalizerError(Exception):
    """Raised for invalid input or option values."""

    def __init__(self, code: Literal["invalid_option", "input_too_large", "invalid_input"]) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class Report:
    """Result of normalization with list of rules that changed the text."""

    text: str
    changed: tuple[str, ...]


_DEFAULT_OPTIONS: Final = Options()


def _validate_input(text: str, max_chars: int) -> None:
    if not isinstance(text, str):
        raise NormalizerError("invalid_input")
    if len(text) > max_chars:
        raise NormalizerError("input_too_large")


def _remove_zero_width(text: str) -> str:
    return text.translate(_ZERO_WIDTH_TRANS)


def _controls(text: str) -> str:
    # Normalize line endings: CRLF and CR become LF.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove C0 and C1 control characters except tab and LF.
    return text.translate(_CONTROL_TRANS)


def _unicode(text: str, form: Literal["NFC", "NFKC"]) -> str:
    return unicodedata.normalize(form, text)


def _quotes(text: str) -> str:
    return text.translate(_QUOTE_TRANS)


def _dashes(text: str) -> str:
    return text.translate(_DASH_TRANS)


def _whitespace(text: str) -> str:
    # Replace all whitespace except LF with space.
    def replace_ws(c: str) -> str:
        if c.isspace() and c != "\n":
            return " "
        return c

    text = "".join(replace_ws(c) for c in text)
    # Collapse runs of spaces.
    text = re.sub(r" +", " ", text)
    # Strip spaces at line starts and ends.
    lines = text.split("\n")
    stripped_lines = [line.strip(" ") for line in lines]
    text = "\n".join(stripped_lines)
    # Collapse 3+ consecutive LFs to two.
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip whole text.
    return text.strip()


def _apply_rules(text: str, options: Options) -> tuple[str, tuple[str, ...]]:
    """Apply normalization rules in fixed order, recording changes."""
    current = text
    changed: list[str] = []

    # zero_width (optional)
    if options.zero_width:
        new = _remove_zero_width(current)
        if new != current:
            changed.append("zero_width")
            current = new

    # controls (always)
    new = _controls(current)
    if new != current:
        changed.append("controls")
        current = new

    # unicode (unless form is 'none')
    form = options.form
    if form != "none":
        new = _unicode(current, form)
        if new != current:
            changed.append("unicode")
            current = new

    # quotes (optional)
    if options.quotes:
        new = _quotes(current)
        if new != current:
            changed.append("quotes")
            current = new

    # dashes (optional)
    if options.dashes:
        new = _dashes(current)
        if new != current:
            changed.append("dashes")
            current = new

    # whitespace (optional)
    if options.whitespace:
        new = _whitespace(current)
        if new != current:
            changed.append("whitespace")
            current = new

    return current, tuple(changed)


def normalize(text: str, options: Options = _DEFAULT_OPTIONS) -> str:
    """Normalize ``text`` according to ``options`` and return the result.

    Raises:
        NormalizerError: if ``text`` is not a string or exceeds ``max_chars``.
    """
    _validate_input(text, options.max_chars)
    result, _ = _apply_rules(text, options)
    return result


def explain(text: str, options: Options = _DEFAULT_OPTIONS) -> Report:
    """Normalize ``text`` and report which rules changed it.

    Returns:
        Report with final text and tuple of rule names that modified the text,
        in the order they were applied.

    Raises:
        NormalizerError: if ``text`` is not a string or exceeds ``max_chars``.
    """
    _validate_input(text, options.max_chars)
    result, changed = _apply_rules(text, options)
    return Report(text=result, changed=changed)
