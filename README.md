# Currency Exchange
🇷🇺 [Читать на русском](README.ru.md)

**Currency Exchange** is a Python 3.12 REST application for managing currencies, exchange rates and currency conversion with SQLite.

Course project: https://zhukovsd.github.io/python-backend-learning-course/projects/currency-exchange/

## Current architecture

This repository is the canonical application:

- Python HTTP backend in src/app/
- SQLite storage for currencies and exchange rates
- embedded UI in src/templates/index.html, served by GET /
- tests in tests/

The separate repository Dimkin33/currency-exchange-frontend is a legacy/reference frontend fork. It still targets an older Java/WAR-style backend contract and is **not** the canonical UI for this application.

The application does not currently fetch live market rates from an external provider. Rates are created and updated through this application's REST API and stored in SQLite.

## API

| Method | Route | Purpose |
| --- | --- | --- |
| GET | / | Embedded UI |
| GET | /currencies | List currencies |
| POST | /currencies | Add currency |
| GET | /currency/:code | Get currency |
| GET | /exchangeRates | List exchange rates |
| POST | /exchangeRates | Add exchange rate |
| GET | /exchangeRate/:pair | Get exchange rate |
| PATCH | /exchangeRate/:pair | Update exchange rate |
| GET | /convert?from=USD&to=EUR&amount=100 | Convert an amount |

Conversion supports a direct rate, a reverse rate, or a route through USD when the required rates exist.

## Setup

    git clone https://github.com/Dimkin33/Currency_Exchange.git
    cd Currency_Exchange
    cp .env.example .env
    bash script/start.sh

The default server address is http://localhost:8000.

Real environment files stay local. Commit only .env.example.

## Tests

Locally:

    bash script/test.sh

GitHub Actions runs the pytest suite on pull requests and pushes to main.

## Project structure

- src/app/ — HTTP server, routing, controllers and models.
- src/templates/ — canonical embedded UI.
- tests/ — model, router and UI/API contract tests.
- script/ — startup, build and test helpers.
- .env.example — safe example configuration.
- pyproject.toml — Python project metadata and commands.
