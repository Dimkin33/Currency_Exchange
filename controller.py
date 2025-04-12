from model import CurrencyModel
from sign_code import currency_sign

class Controller:
    def __init__(self):
        self.model = CurrencyModel()

    def get_currencies(self, dto):
        currencies = self.model.get_currencies()
        dto.response = {"currencies": currencies}

    def get_currency_by_code(self, dto):
        print('Hello')
        code = dto.query_params.get('code', [None])[0]
        if not code:
            dto.response = {"error": "Currency code is required"}
            return
        currency = self.model.get_currency_by_code(code)
        if currency:
            dto.response = {"currency": currency}
        else:
            dto.response = {"error": "Currency not found"}

    def add_currency(self, dto):
        code = dto.body.get('code')
        name = dto.body.get('name')
        sign = dto.body.get('sign')
        if not code or not name or not sign:
            dto.response = {"error": "Missing required fields"}
            return
        try:
            self.model.add_currency(code, name, sign)
            dto.response = {"message": f"Currency {code} added successfully"}
        except ValueError as e:
            dto.response = {"error": str(e)}

    def get_exchange_rates(self, dto):
        rates = self.model.get_exchange_rates()
        dto.response = {"exchange_rates": rates}

    def add_exchange_rate(self, dto):
        from_currency = dto.body.get('from')
        to_currency = dto.body.get('to')
        rate = dto.body.get('rate')
        if not from_currency or not to_currency or not rate:
            dto.response = {"error": "Missing required fields"}
            return
        try:
            self.model.add_exchange_rate(from_currency, to_currency, float(rate))
            dto.response = {"message": f"Exchange rate from {from_currency} to {to_currency} added successfully"}
        except ValueError as e:
            dto.response = {"error": str(e)}

    def convert_currency(self, dto):
        from_currency = dto.query_params.get('from', [None])[0]
        to_currency = dto.query_params.get('to', [None])[0]
        amount = dto.query_params.get('amount', [None])[0]
        if not from_currency or not to_currency or not amount:
            dto.response = {"error": "Missing required parameters"}
            return
        try:
            amount = float(amount)
            converted_amount = self.model.convert_currency(from_currency, to_currency, amount)
            dto.response = {"converted_amount": converted_amount}
        except ValueError as e:
            dto.response = {"error": str(e)}

    def handle_html_page(self, dto):
        try:
            with open('index.html', 'r', encoding='utf-8') as file:
                html_content = file.read()
            dto.response = html_content
        except FileNotFoundError:
            dto.response = {"error": "HTML file not found"}

