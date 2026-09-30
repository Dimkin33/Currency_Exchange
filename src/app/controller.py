import logging
import os
import sqlite3
from pathlib import Path

from db_initializer import init_db
from dotenv import load_dotenv
from errors import (
    CurrencyNotFoundError,
    InvalidAmountFormatError,
    MissingFormFieldError,
    UnknownCurrencyCodeError,
)
from market_rates import FrankfurterClient
from model import ConversionModel, CurrencyModel, ExchangeRateModel
from sign_code import currency_sign

logger = logging.getLogger(__name__)


class Controller:
    """Контроллер для обработки запросов и взаимодействия с моделями."""

    def __init__(self, db_path: str = None):
        logger.info('Инициализация контроллера')
        load_dotenv()
        if db_path is None:
            db_path = os.getenv('DB_PATH', 'currency.db')

        self.connector = sqlite3.connect(db_path, uri=True)
        init_db(self.connector)

        self.currency_model = CurrencyModel(connector=self.connector)
        self.exchange_rate_model = ExchangeRateModel(connector=self.connector)
        self.conversion_model = ConversionModel(connector=self.connector)
        logger.info(
            f'Инициализация моделей с коннектором {self.connector}, путь к БД: {db_path}'
        )

    def close(self) -> None:
        connector = getattr(self, 'connector', None)
        if connector is not None:
            try:
                connector.close()
            finally:
                self.connector = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def health(self) -> dict:
        return {
            'status': 'ok',
            'marketProvider': 'Frankfurter',
            'autoRefresh': os.getenv('MARKET_AUTO_REFRESH', 'true').lower()
            in {'1', 'true', 'yes', 'on'},
        }, 200

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

    def _ensure_currency(self, code: str) -> dict:
        code = code.upper()
        currency = currency_sign.get(code)
        if not currency:
            raise UnknownCurrencyCodeError(code)

        try:
            return self.currency_model.get_currency_by_code(code)
        except CurrencyNotFoundError:
            name, sign = currency
            return self.currency_model.add_currency(code, name, sign)

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
        except (TypeError, ValueError) as e:
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
        try:
            rate = float(rate)
        except (TypeError, ValueError) as e:
            raise InvalidAmountFormatError() from e
        return self.exchange_rate_model.patch_exchange_rate(
            from_currency, to_currency, rate
        ), 200

    def get_exchange_rates(self) -> list[dict]:
        return self.exchange_rate_model.get_exchange_rates(), 200

    def sync_market_rates(self, base: str = None, quotes: str = None) -> dict:
        base = (base or os.getenv('MARKET_BASE_CURRENCY', 'USD')).strip().upper()

        raw_quotes = quotes or os.getenv(
            'MARKET_QUOTES', 'EUR,GBP,RUB,JPY,CHF,CNY'
        )
        quote_codes = [
            item.strip().upper()
            for item in raw_quotes.split(',')
            if item.strip()
        ]
        quote_codes = list(dict.fromkeys(quote_codes))
        quote_codes = [code for code in quote_codes if code != base]

        if not quote_codes:
            raise MissingFormFieldError()

        if base not in currency_sign:
            raise UnknownCurrencyCodeError(base)
        for code in quote_codes:
            if code not in currency_sign:
                raise UnknownCurrencyCodeError(code)

        client = FrankfurterClient()

        fetched = [client.get_rate(base, quote) for quote in quote_codes]

        self._ensure_currency(base)
        for code in quote_codes:
            self._ensure_currency(code)

        updated_rates = []
        provider_dates = []
        for item in fetched:
            updated_rates.append(
                self.exchange_rate_model.upsert_exchange_rate(
                    item['base'], item['quote'], item['rate']
                )
            )
            if item.get('date'):
                provider_dates.append(item['date'])

        return {
            'provider': client.provider_name,
            'base': base,
            'quotes': quote_codes,
            'asOf': max(provider_dates) if provider_dates else None,
            'updated': len(updated_rates),
            'rates': updated_rates,
        }, 200

    def convert_currency(
        self, from_currency: str, to_currency: str, amount: float
    ) -> dict:
        if not from_currency or not to_currency or not amount:
            raise MissingFormFieldError()
        try:
            amount = float(amount)
        except (TypeError, ValueError) as e:
            raise InvalidAmountFormatError() from e

        return self.conversion_model.get_converted_currency(
            from_currency, to_currency, amount
        ), 200

    def handle_html_page(self) -> str:
        template_path = Path(__file__).parent.parent / 'templates' / 'index.html'
        logger.info(f'Путь к шаблону: {template_path}')
        if not Path(template_path).exists():
            raise FileNotFoundError('HTML-шаблон не найден')
        return template_path.read_text(encoding='utf-8'), 200

    def return_icon(self) -> bytes:
        template_path = Path(__file__).parent.parent / 'templates' / 'favicon.ico'
        if not Path(template_path).exists():
            raise FileNotFoundError('favicon.ico не найден')
        with open(template_path, 'rb') as f:
            return f.read(), 200
