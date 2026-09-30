# AGENTS.md

## Project boundary

This repository is the canonical Currency Exchange application for the Dimkin33 Agent Hub instance.

The related repository Dimkin33/currency-exchange-frontend is a legacy/reference frontend fork. Do not make it the runtime UI or change it as part of ordinary Currency Exchange work unless the user explicitly requests that repository.

## Canonical surfaces

- Backend: src/app/
- Embedded UI: src/templates/index.html
- Market provider adapter: src/app/market_rates.py
- Tests: tests/
- Environment template: .env.example

The embedded UI must use the same route contract implemented by src/app/router.py.

## API contract

Primary routes:

- GET /health
- GET /
- GET /currencies
- POST /currencies
- GET /currency/:code
- GET /exchangeRates
- POST /exchangeRates
- POST /exchangeRates/sync
- GET /exchangeRate/:pair
- PATCH /exchangeRate/:pair
- GET /convert

When changing the UI or router, update or add contract tests so route drift is caught in CI.

## Market-rate contract

Frankfurter v2 is the default public provider and requires no repository secret.

Default synchronization stores USD-based pairs because cross-conversion in model/conversion.py derives rates through USD.

Provider failures must be surfaced as a bounded API error and must not expose credentials or internal state.

## Validation

Use Python 3.12.

Run:

    PYTHONPATH=src/app python -m pytest -q

Pull requests and pushes to main are validated by .github/workflows/ci.yml.

## Security

Never commit a real .env, credentials, tokens, passwords or session material. Only .env.example is repository configuration.

## Change policy

Prefer branch -> tests -> pull request -> merge. Current branch, PR and CI state must be read live from GitHub.
