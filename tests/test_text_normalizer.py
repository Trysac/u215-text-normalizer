"""Tests for text_normalizer."""

from __future__ import annotations

import io
import random
import sys

import pytest

from text_normalizer import NormalizerError, Options, explain, normalize
from text_normalizer.__main__ import main


def test_acceptance_1() -> None:
    assert (
        normalize("\ufeff\u201cHello\u201d\u00a0world \u2014 it\u2019s \ufb01ne")
        == '"Hello" world - it\'s fine'
    )


def test_acceptance_2() -> None:
    assert normalize("  a\t\tb  \n\n\n\nc \r\n") == "a b\n\nc"


def test_acceptance_3() -> None:
    assert normalize("co\u200bop\u00aderate") == "cooperate"
    assert normalize("\U0001f469\u200d\U0001f4bb") == "\U0001f469\u200d\U0001f4bb"


def test_acceptance_4() -> None:
    assert normalize("\u201ca\u201d", Options(quotes=False)) == "\u201ca\u201d"
    assert normalize("\ufb01", Options(form="NFC")) == "\ufb01"
    with pytest.raises(NormalizerError) as exc_info:
        Options(form="NFKD")
    assert exc_info.value.code == "invalid_option"


def test_acceptance_5() -> None:
    assert explain("\u201ca\u201d").changed == ("quotes",)
    assert explain("\uff41").changed == ("unicode",)
    assert explain("plain").changed == ()


def test_acceptance_6() -> None:
    with pytest.raises(NormalizerError) as exc_info:
        normalize("a" * 10_000_001, Options(max_chars=10_000_000))
    assert exc_info.value.code == "input_too_large"
    # 10_000_000 characters accepted.
    normalize("a" * 10_000_000, Options(max_chars=10_000_000))


def test_acceptance_7() -> None:
    examples = [
        "\ufeff\u201cHello\u201d\u00a0world \u2014 it\u2019s \ufb01ne",
        "  a\t\tb  \n\n\n\nc \r\n",
        "co\u200bop\u00aderate",
        "\U0001f469\u200d\U0001f4bb",
        "\u201ca\u201d",
        "\ufb01",
        "plain",
    ]
    for text in examples:
        once = normalize(text)
        twice = normalize(once)
        assert twice == once

    # CLI acceptance: --no-quotes reads stdin, writes stdout, returns 0.
    old_stdin = sys.stdin
    sys.stdin = io.StringIO("\u201ca\u201d")
    try:
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        try:
            ret = main(["--no-quotes"])
        finally:
            sys.stdout = old_stdout
    finally:
        sys.stdin = old_stdin
    assert ret == 0
    assert new_stdout.getvalue() == "\u201ca\u201d"

    # Unknown flag returns 2.
    assert main(["--unknown"]) == 2


def test_empty_string() -> None:
    assert normalize("") == ""
    assert explain("").changed == ()


def test_whitespace_only() -> None:
    assert normalize("   \t\n  ") == ""
    report = explain("   \t\n  ")
    assert report.text == ""
    assert report.changed == ("whitespace",)


def test_tabs_inside_line() -> None:
    assert normalize("a\tb") == "a b"


def test_combining_accent_nfc_vs_none() -> None:
    text = "e\u0301"  # e + combining acute accent
    assert normalize(text, Options(form="NFC")) == "\u00e9"
    assert normalize(text, Options(form="none")) == text


def test_minus_sign() -> None:
    assert normalize("\u2212") == "-"
    assert normalize("\u2212", Options(dashes=False)) == "\u2212"


def test_options_invalid_form() -> None:
    with pytest.raises(NormalizerError) as exc_info:
        Options(form="invalid")
    assert exc_info.value.code == "invalid_option"


def test_options_invalid_max_chars() -> None:
    with pytest.raises(NormalizerError):
        Options(max_chars=-1)
    with pytest.raises(NormalizerError):
        Options(max_chars="100")  # type: ignore[arg-type]


def test_normalize_invalid_input() -> None:
    with pytest.raises(NormalizerError) as exc_info:
        normalize(123)  # type: ignore[arg-type]
    assert exc_info.value.code == "invalid_input"


def test_idempotence_all_options() -> None:
    alphabet = (
        "a b c\t\n\r"
        "\u200b\u2060\ufeff\u00ad"
        "\u2018\u2019\u201c\u201d\u201a\u201b\u201e\u201f"
        "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"
        "\u00a0\u2000\u2001\ufb01\uff41"
        "\u0000\u0001\u007f\u0080\u009f"
    )
    rng = random.Random(0)  # noqa: S311
    forms = ["NFC", "NFKC", "none"]
    for form in forms:
        for quotes in (True, False):
            for dashes in (True, False):
                for whitespace in (True, False):
                    for zero_width in (True, False):
                        opts = Options(
                            form=form,
                            quotes=quotes,
                            dashes=dashes,
                            whitespace=whitespace,
                            zero_width=zero_width,
                        )
                        for _ in range(1000):
                            s = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 50)))
                            assert normalize(normalize(s, opts), opts) == normalize(s, opts)


def test_explain_multiple_rules_order() -> None:
    text = "\ufeff\u201cHello\u201d\u00a0world \u2014 it\u2019s \ufb01ne\t x \r\n"
    report = explain(text)
    assert report.changed == (
        "zero_width",
        "controls",
        "unicode",
        "quotes",
        "dashes",
        "whitespace",
    )


def test_main_default(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("\u201cHello\u201d"))
    ret = main([])
    captured = capsys.readouterr()
    assert ret == 0
    assert captured.out == '"Hello"'
    assert captured.err == ""


def test_main_no_quotes(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("\u201ca\u201d"))
    ret = main(["--no-quotes"])
    captured = capsys.readouterr()
    assert ret == 0
    assert captured.out == "\u201ca\u201d"
    assert captured.err == ""


def test_main_explain(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("\u201ca\u201d"))
    ret = main(["--explain"])
    captured = capsys.readouterr()
    assert ret == 0
    assert captured.out == '"a"'
    assert captured.err == "quotes\n"


def test_main_unknown_flag(capsys: pytest.CaptureFixture[str]) -> None:
    ret = main(["--unknown"])
    capsys.readouterr()
    assert ret == 2
    # argparse prints usage to stderr; no assertion on content.


def test_main_input_too_large(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    import text_normalizer.__main__ as main_mod

    def fake_normalize(text: str, options: Options) -> str:
        raise NormalizerError("input_too_large")

    monkeypatch.setattr(main_mod, "normalize", fake_normalize)
    monkeypatch.setattr("sys.stdin", io.StringIO("x"))
    ret = main([])
    captured = capsys.readouterr()
    assert ret == 2
    assert "input too large" in captured.err
