from controller import Controller

class Router:
    def __init__(self):
        self.routes = {
            '/currencies': Controller().get_currencies,
            '/currency': Controller().get_currency_by_code,
            '/exchangeRates': Controller().get_exchange_rates,
            '/addCurrency': Controller().add_currency,
            '/addExchangeRate': Controller().add_exchange_rate,
            '/': Controller().handle_html_page,
        }

    def resolve(self, dto):
        # Используем dto.url для определения маршрута
        handler = self.routes.get(dto.url, None)
        if handler:
            handler(dto)
        else:
            dto.response = {"error": "Route not found"}


