# Architecture

## Rule Application

`normalize` and `explain` apply a fixed sequence of transformations to the input string.
Each transformation is a pure function that returns a new string (or the same string if no
change). The order ensures idempotence: once a rule has made its change, subsequent rules
cannot introduce a character that an earlier rule would modify again.

- **zero_width** removes invisible characters (except ZWJ/ZWNJ).
- **controls** normalizes line endings and strips control characters.
- **unicode** applies `unicodedata.normalize` (NFKC by default) which may combine
  characters or map compatibility forms.
- **quotes** and **dashes** use translation tables for fast replacement.
- **whitespace** is applied last because it collapses spaces and strips text; if it ran
  before unicode, characters like NBSP would not be handled consistently.

The `Report` returned by `explain` lists the names of rules that actually changed the text,
in the order they were applied.

## Error Handling

`NormalizerError` is the single exception type, with a machine-readable `code`. Input
validation checks that the argument is a string and respects `max_chars` before processing.
No logging configuration is imposed; the module uses a `NullHandler` to avoid interfering
with applications.

## CLI

The `__main__` module reads UTF-8 from stdin, writes normalized text to stdout, and optionally
prints the changed rule names to stderr when `--explain` is given. Exit code 0 indicates
success; 2 indicates usage errors or input too large.
