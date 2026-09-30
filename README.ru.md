# Currency Exchange

**Currency Exchange** — учебное приложение на Python 3.12 для управления валютами, курсами и конвертацией. Данные хранятся в SQLite, поверх них работает REST API.

Задание: https://zhukovsd.github.io/python-backend-learning-course/projects/currency-exchange/

## Текущая архитектура

Этот репозиторий является каноническим приложением:

- backend находится в src/app/
- валюты и курсы хранятся в SQLite
- основной UI находится в src/templates/index.html и отдаётся через GET /
- рыночные курсы синхронизируются через публичный Frankfurter v2
- тесты автоматически запускаются в GitHub Actions

Отдельный репозиторий Dimkin33/currency-exchange-frontend оставлен как старый/reference frontend-форк и не используется как текущий UI.

## Актуальные рыночные курсы

Приложение использует публичный Frankfurter v2. API-ключ не нужен.

По умолчанию при запуске и затем каждые шесть часов обновляются пары:

    USD -> EUR, GBP, RUB, JPY, CHF, CNY

USD выбран базой специально: существующая модель конвертации умеет строить кросс-курс через USD. Например, имея USD/EUR и USD/RUB, приложение может посчитать EUR/RUB без отдельной записи EUR/RUB.

Настройки:

    MARKET_API_URL=https://api.frankfurter.dev/v2
    MARKET_AUTO_REFRESH=true
    MARKET_REFRESH_SECONDS=21600
    MARKET_BASE_CURRENCY=USD
    MARKET_QUOTES=EUR,GBP,RUB,JPY,CHF,CNY

Обновление можно запустить вручную:

    POST /exchangeRates/sync

Параметры base и quotes опциональны; quotes передаётся списком через запятую.

## API

| Метод | Маршрут | Назначение |
| --- | --- | --- |
| GET | /health | Проверка состояния |
| GET | / | Встроенный UI |
| GET | /currencies | Список валют |
| POST | /currencies | Добавление валюты |
| GET | /currency/:code | Получение валюты |
| GET | /exchangeRates | Список курсов |
| POST | /exchangeRates | Добавление курса |
| POST | /exchangeRates/sync | Обновление курсов из Frankfurter |
| GET | /exchangeRate/:pair | Получение курса |
| PATCH | /exchangeRate/:pair | Изменение курса |
| GET | /convert?from=USD&to=EUR&amount=100 | Конвертация суммы |

Конвертация использует прямой курс, обратный курс либо пересчёт через USD.

## Запуск

    git clone https://github.com/Dimkin33/Currency_Exchange.git
    cd Currency_Exchange
    cp .env.example .env
    bash script/start.sh

По умолчанию локальный сервер доступен на http://localhost:8000.

Настоящий .env должен оставаться локальным; в Git хранится только безопасный .env.example.

## Тестирование

Локально:

    bash script/test.sh

GitHub Actions запускает pytest для pull request и push в main.

## Структура

- src/app/ — HTTP-сервер, роутер, контроллеры, клиент рыночных курсов и модели.
- src/templates/ — канонический встроенный UI.
- tests/ — тесты моделей, роутера, провайдера и UI/API-контракта.
- script/ — скрипты запуска, сборки и тестов.
- .env.example — безопасный пример конфигурации.
- pyproject.toml — настройки Python-проекта.
