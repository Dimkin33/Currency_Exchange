# Currency Exchange

**Currency Exchange** — учебное приложение на Python 3.12 для управления валютами, курсами и конвертацией. Данные хранятся в SQLite, поверх них работает REST API.

Задание: https://zhukovsd.github.io/python-backend-learning-course/projects/currency-exchange/

## Текущая архитектура

Этот репозиторий является каноническим приложением:

- backend находится в src/app/
- валюты и курсы хранятся в SQLite
- основной UI находится в src/templates/index.html и отдаётся через GET /
- тесты находятся в tests/

Отдельный репозиторий Dimkin33/currency-exchange-frontend оставлен как старый/reference frontend-форк. Он рассчитан на прежний Java/WAR-контракт и **не является текущим frontend** этого проекта.

Сейчас приложение не загружает рыночные курсы автоматически из внешнего сервиса. Курсы добавляются и обновляются через REST API самого приложения и сохраняются в SQLite.

## API

| Метод | Маршрут | Назначение |
| --- | --- | --- |
| GET | / | Встроенный UI |
| GET | /currencies | Список валют |
| POST | /currencies | Добавление валюты |
| GET | /currency/:code | Получение валюты |
| GET | /exchangeRates | Список курсов |
| POST | /exchangeRates | Добавление курса |
| GET | /exchangeRate/:pair | Получение курса |
| PATCH | /exchangeRate/:pair | Изменение курса |
| GET | /convert?from=USD&to=EUR&amount=100 | Конвертация суммы |

Конвертация использует прямой курс, обратный курс либо пересчёт через USD, если нужные курсы есть в базе.

## Запуск

    git clone https://github.com/Dimkin33/Currency_Exchange.git
    cd Currency_Exchange
    cp .env.example .env
    bash script/start.sh

По умолчанию сервер запускается на http://localhost:8000.

Настоящий .env должен оставаться локальным; в Git хранится только безопасный .env.example.

## Тестирование

Локально:

    bash script/test.sh

GitHub Actions запускает pytest для pull request и push в main.

## Структура

- src/app/ — HTTP-сервер, роутер, контроллеры и модели.
- src/templates/ — канонический встроенный UI.
- tests/ — тесты моделей, роутера и UI/API-контракта.
- script/ — скрипты запуска, сборки и тестов.
- .env.example — безопасный пример конфигурации.
- pyproject.toml — настройки Python-проекта.
