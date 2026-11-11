# Project record

## Objective

Normalize text for indexing with an explicit, ordered rule set: zero-width removal, control characters, Unicode NFKC, curly quotes, dashes and whitespace, idempotent

## Scope

- In scope: the public API documented in [README.md](../README.md), typed and tested.
- Out of scope: anything that needs runtime dependencies or I/O without an accepted ADR.

## Timeline

| Date | Event |
|---|---|
| 2026 | Repository created from the factory utility template. |

## Effort metrics

Measured values only; a value that has not been measured stays "pending measurement".

| Metric | Value |
|---|---|
| Tokens (input / output) | 221333 / 36257 |
| Hours (human) | pending measurement |
| Cost (USD) | 0.0571 |

## Factory run u215 (measured from API usage)

| Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|
| generation | deepseek-v4-pro | yes | 3456 | 14844 | 0 | 1280 | 0.0317 |
| fix-1 | deepseek-flash | no | 7251 | 2239 | 0 | 37632 | 0.0025 |
| fix-2 | deepseek-flash | no | 4993 | 596 | 0 | 23040 | 0.0012 |
| fix-3 | deepseek-flash | no | 12915 | 1928 | 0 | 54528 | 0.0033 |
| fix-4 | deepseek-flash | no | 633 | 650 | 0 | 20352 | 0.0005 |
| docs | deepseek-flash | no | 54997 | 16000 | 0 | 256 | 0.0179 |

Total: $0.0571. Prices: deepseek line, as measured by its adapter.
