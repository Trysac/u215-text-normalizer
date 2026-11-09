# Ordered rule set for text normalization with report

Status: accepted (generated, pending human review)

## Context

Text from various sources contains invisible characters, non-breaking spaces, curly quotes, ligatures, and stray control codes. Ad hoc cleanup functions vary and often forget which characters they change.

## Decision

Implement a small, documented, ordered set of rules (zero-width removal, control characters, Unicode normalization, quote/dash mapping, whitespace normalization) with an explain function that reports which rules changed the text.

## Consequences

The library has no runtime dependencies, is idempotent, and provides an explicit report. It intentionally does not handle transliteration, case folding, or diacritic removal, which are left to higher-level analyzers.
