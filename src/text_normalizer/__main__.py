"""Command-line interface for text normalization."""

from __future__ import annotations

import argparse
import sys

from . import NormalizerError, Options, explain, normalize


def _build_options(args: argparse.Namespace) -> Options:
    return Options(
        form=args.form,
        quotes=not args.no_quotes,
        dashes=not args.no_dashes,
        whitespace=not args.no_whitespace,
        zero_width=not args.no_zero_width,
    )


def main(argv: list[str] | None = None) -> int:
    """Run the CLI.

    Returns:
        Exit code: 0 on success, 2 on usage error or input too large.
    """
    parser = argparse.ArgumentParser(
        prog="text-normalizer", description="Normalize text for indexing."
    )
    parser.add_argument("--form", choices=["NFC", "NFKC", "none"], default="NFKC")
    parser.add_argument("--no-quotes", action="store_true")
    parser.add_argument("--no-dashes", action="store_true")
    parser.add_argument("--no-whitespace", action="store_true")
    parser.add_argument("--no-zero-width", action="store_true")
    parser.add_argument("--explain", action="store_true")

    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2

    try:
        input_text = sys.stdin.read()
        options = _build_options(args)
        if args.explain:
            report = explain(input_text, options)
            for rule in report.changed:
                print(rule, file=sys.stderr)
            sys.stdout.write(report.text)
        else:
            sys.stdout.write(normalize(input_text, options))
    except NormalizerError as exc:
        if exc.code == "input_too_large":
            print("input too large", file=sys.stderr)
        return 2
    except Exception:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
