import logging
import os
import sqlite3
from pathlib import Path

from db_initializer import init_db
from dotenv import load_dotenv
from errors import (
    InvalidAmountFormatError,
    MissingFormFieldError,
    UnknownCurrencyCodeError,
)
from model import ConversionModel, CurrencyModel, ExchangeRateModel
from sign_code import currency_sign

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, db_path: str = None):
        logger.info('Инициализация контроллера')
        # Загрузка переменных окружения
        load_dotenv()
        if db_path is None:
            # Если путь к БД не передан, берем его из переменной окружения
            db_path = os.getenv('DB_PATH', 'currency.db')

        # Если переменная окружения не задана, используем значение по умолчанию

        self.connector = sqlite3.connect(db_path, uri=True)  # Подключение к базе данных
        init_db(self.connector)

        # Инициализация моделей
        self.currency_model = CurrencyModel(connector=self.connector)
        self.exchange_rate_model = ExchangeRateModel(connector=self.connector)
        self.conversion_model = ConversionModel(connector=self.connector)
        logger.info(
            f'Инициализация моделей с коннектором {self.connector}, путь к БД: {db_path}'
        )

    def __del__(self):  # Закрытие соединения с БД
        logger.info('Закрытие соединения с БД')
        try:
            self.currency_model.connector.close()
        except Exception:
            pass

    def get_currency_by_code(self, code: str) -> dict:
        if not code:
            raise MissingFormFieldError()
        return self.currency_model.get_currency_by_code(code.upper()), 200

    def delete_all_currencies(self) -> bool:
        return self.currency_model.delete_all_currencies(), 200

    def get_currencies(self) -> list[dict]:
        return self.currency_model.get_currencies(), 200

    def add_currency(self, code: str, name: str) -> dict:
        if not code:
            raise MissingFormFieldError()

        code = code.upper()
        currency = currency_sign.get(code)
        if not currency:
            raise UnknownCurrencyCodeError(code)
        if not name:
            name, sign = currency
        else:
            sign = currency[1]

        return self.currency_model.add_currency(code, name, sign), 201

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> dict:
        if not from_currency or not to_currency:
            raise MissingFormFieldError()
        return self.exchange_rate_model.get_exchange_rate(
            from_currency, to_currency
        ), 200

    def add_exchange_rate(
        self, from_currency: str, to_currency: str, rate: float
    ) -> dict:
        try:
            rate = float(rate)
        except ValueError as e:
            raise InvalidAmountFormatError() from e
        if not from_currency or not to_currency or not rate:
            raise MissingFormFieldError()
        return self.exchange_rate_model.add_exchange_rate(
            from_currency.upper(), to_currency.upper(), rate
        ), 201

    def update_exchange_rate(
        self, from_currency: str, to_currency: str, rate: float
    ) -> dict:
        if not from_currency or not to_currency or not rate:
            raise MissingFormFieldError()
        return self.exchange_rate_model.patch_exchange_rate(
            from_currency, to_currency, rate
        ), 200

    def get_exchange_rates(self) -> list[dict]:
        return self.exchange_rate_model.get_exchange_rates(), 200

    def convert_currency(
        self, from_currency: str, to_currency: str, amount: float
    ) -> dict:
        if not from_currency or not to_currency or not amount:
            raise MissingFormFieldError()
        try:
            amount = float(amount)
        except ValueError as e:
            raise InvalidAmountFormatError() from e

        return self.conversion_model.get_converted_currency(
            from_currency, to_currency, amount
        ), 200

    def handle_html_page(self) -> str:
        """Возвращает HTML-страницу"""
        # Проверяем, существует ли файл index.html
        template_path = Path(__file__).parent.parent / 'templates' / 'index.html'
        logger.info(f'Путь к шаблону: {template_path}')
        if not Path(template_path).exists():
            raise FileNotFoundError('HTML-шаблон не найден')
        # Читаем содержимое файла index.html
        return template_path.read_text(encoding='utf-8'), 200

    def return_icon(self) -> bytes:
        template_path = Path(__file__).parent.parent / 'templates' / 'favicon.ico'
        if not Path(template_path).exists():
            raise FileNotFoundError('favicon.ico не найден')
        with open(template_path, 'rb') as f:
            return f.read(), 200
