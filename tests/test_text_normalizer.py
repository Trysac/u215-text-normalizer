"""Behavior tests for the public API of text_normalizer."""

from __future__ import annotations

import pytest

import text_normalizer


def test_normalize_trims_and_lowercases() -> None:
    assert text_normalizer.normalize("  Hello World ") == "hello world"


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_normalize_rejects_blank_input(value: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        text_normalizer.normalize(value)


def test_version_is_semver() -> None:
    parts = text_normalizer.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
