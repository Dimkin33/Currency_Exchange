# Currency Exchange
🇷🇺 [Читать на русском](README.ru.md)

**Currency Exchange** is a Python 3.12 REST application for currencies, exchange rates and conversion with SQLite.

Course project: https://zhukovsd.github.io/python-backend-learning-course/projects/currency-exchange/

## Current architecture

This repository is the canonical application:

- Python HTTP backend in src/app/
- SQLite storage for currencies and exchange rates
- embedded UI in src/templates/index.html, served by GET /
- public market-rate synchronization through Frankfurter v2
- tests and GitHub Actions CI

The separate repository Dimkin33/currency-exchange-frontend is a legacy/reference frontend fork and is not the runtime UI.

## Live market rates

The application uses the public Frankfurter v2 API. No API key is required.

By default it refreshes these USD-based pairs on startup and every six hours:

    USD -> EUR, GBP, RUB, JPY, CHF, CNY

USD is the default market base because the existing conversion model can derive cross-rates through USD. For example, if USD/EUR and USD/RUB are stored, EUR/RUB conversion can be derived without storing a separate EUR/RUB pair.

Configuration is controlled by:

    MARKET_API_URL=https://api.frankfurter.dev/v2
    MARKET_AUTO_REFRESH=true
    MARKET_REFRESH_SECONDS=21600
    MARKET_BASE_CURRENCY=USD
    MARKET_QUOTES=EUR,GBP,RUB,JPY,CHF,CNY

A refresh can also be triggered manually:

    POST /exchangeRates/sync

Optional form/query fields are base and quotes, where quotes is a comma-separated list.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| GET | /health | Health check |
| GET | / | Embedded UI |
| GET | /currencies | List currencies |
| POST | /currencies | Add currency |
| GET | /currency/:code | Get currency |
| GET | /exchangeRates | List exchange rates |
| POST | /exchangeRates | Add exchange rate |
| POST | /exchangeRates/sync | Refresh rates from Frankfurter |
| GET | /exchangeRate/:pair | Get exchange rate |
| PATCH | /exchangeRate/:pair | Update exchange rate |
| GET | /convert?from=USD&to=EUR&amount=100 | Convert an amount |

Conversion supports a direct rate, a reverse rate, or a route through USD when the required rates exist.

## Setup

    git clone https://github.com/Dimkin33/Currency_Exchange.git
    cd Currency_Exchange
    cp .env.example .env
    bash script/start.sh

The default local address is http://localhost:8000.

Real environment files stay local. Commit only .env.example.

## Tests

Locally:

    bash script/test.sh

GitHub Actions runs the pytest suite on pull requests and pushes to main.

## Project structure

- src/app/ — HTTP server, routing, controllers, market-rate client and models.
- src/templates/ — canonical embedded UI.
- tests/ — model, router, provider and UI/API contract tests.
- script/ — startup, build and test helpers.
- .env.example — safe example configuration.
- pyproject.toml — Python project metadata and commands.
