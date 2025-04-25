import logging
from model import CurrencyModel
from sign_code import currency_sign
from errors import MissingFormFieldError, UnknownCurrencyCodeError, InvalidAmountFormatError

logger = logging.getLogger(__name__)

class Controller:
    def __init__(self, connector):
        self.model = CurrencyModel(connector = connector)

    def get_currency_by_code(self, code: str) -> dict:
        if not code:
            raise MissingFormFieldError()
        return self.model.get_currency_by_code(code)

    def delete_all_currencies(self) -> bool:
        return self.model.delete_all_currencies()
    
    def get_currencies(self) -> list[dict]:
        return self.model.get_currencies()

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
        
        return self.model.add_currency(code, name, sign)

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> dict:
        if not from_currency or not to_currency:
            raise MissingFormFieldError()
        return self.model.get_exchange_rate(from_currency, to_currency)

    def add_exchange_rate(self, from_currency: str, to_currency: str, rate: float) -> dict:
        try:
            rate = float(rate)
        except ValueError:
            raise InvalidAmountFormatError()
        if not from_currency or not to_currency or not rate:
            raise MissingFormFieldError()
        return self.model.add_exchange_rate(from_currency.upper(), to_currency.upper(), rate)

    def update_exchange_rate(self, from_currency: str, to_currency: str, rate: float) -> dict:
        if not from_currency or not to_currency or not rate:
            raise MissingFormFieldError()
        return self.model.patch_exchange_rate(from_currency, to_currency, rate)

    def get_exchange_rates(self) -> list[dict]:
        return self.model.get_exchange_rates()

    def convert_currency(self, from_currency: str, to_currency: str, amount: float) -> dict:
        if not from_currency or not to_currency or not amount:
            raise MissingFormFieldError()
        try:
            amount = float(amount)
        except ValueError:
            raise InvalidAmountFormatError()

        return self.model.get_converted_currency(from_currency, to_currency, amount)

    def handle_html_page(self) -> str:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
        
    def return_icon(self) -> bytes:
        with open("favicon.ico", "rb") as f:
            return f.read()