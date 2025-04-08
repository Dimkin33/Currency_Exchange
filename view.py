from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from model import CurrencyModel
import os

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.model = CurrencyModel()
        super().__init__(*args, **kwargs)

    def send_json_response(self, status_code, data):
        """Отправляет JSON-ответ с указанным статусом и данными."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


    def do_GET(self):
        if self.path.startswith('/currency/'):  # Проверяем, начинается ли путь с /currency/
            self.handle_get_currency_by_code()  # Обработчик для получения конкретной валюты
        elif self.path == '/currencies':
            self.handle_get_currencies()
        elif self.path == '/exchangeRates':  # Изменен маршрут на /exchangeRates
            self.handle_get_exchange_rates()
        elif self.path == '/':
            self.handle_html_page()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/currencies':
            self.handle_add_currency()
        elif self.path == '/exchangeRates':
            self.handle_add_exchange_rate()
        elif self.path == '/convert':
            self.handle_convert_currency()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_get_currencies(self):
        currencies = self.model.get_currencies()  # Получаем список словарей
        self.send_json_response(200, currencies)  # Используем send_json_response

    def handle_add_currency(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        try:
            self.model.add_currency(data['code'], data['name'])
            self.send_json_response(201, {'message': 'Currency added successfully'})
        except ValueError as e:
            self.send_json_response(400, {'error': str(e)})

    def handle_get_exchange_rates(self):
        rates = self.model.get_exchange_rates()
        self.send_json_response(200, rates)  # Используем send_json_response

    def handle_add_exchange_rate(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        try:
            self.model.add_exchange_rate(data['from'], data['to'], data['rate'])
            self.send_json_response(201, {'message': 'Exchange rate added successfully'})
        except ValueError as e:
            self.send_json_response(400, {'error': str(e)})

    def handle_convert_currency(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        try:
            converted_amount = self.model.convert_currency(data['from'], data['to'], data['amount'])
            self.send_json_response(200, {'converted_amount': converted_amount})
        except ValueError as e:
            self.send_json_response(400, {'error': str(e)})

    def handle_html_page(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open('index.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
        self.wfile.write(html_content.encode())

    def handle_get_currency_by_code(self):
        try:
            # Извлекаем код валюты из URL
            code = self.path.split('/currency/')[1]
            if not code:
                self.send_json_response(400, {'error': 'Currency code is required'})
                return

            # Получаем данные валюты из модели
            currency = self.model.get_currency_by_code(code)
            if not currency:
                self.send_json_response(404, {'error': 'Currency not found 2 '})
                return
            # Формируем успешный ответ
            self.send_json_response(200, {
                'id': 0,  # ID можно заменить на реальный, если он есть в базе данных
                'name': currency['name'],
                'code': currency['code'],
                'sign': currency.get('sign', '')  # Если знак валюты есть в данных
            })
        except Exception as e:
            # Обработка ошибок
            self.send_json_response(500, {'error': 'Internal server error', 'details': str(e)})

def start_server():
    server = HTTPServer(('localhost', 8000), RequestHandler)
    print('Server running on http://localhost:8000')
    server.serve_forever()