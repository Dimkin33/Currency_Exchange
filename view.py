from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from model import CurrencyModel
import os

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.model = CurrencyModel()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/currencies':
            self.handle_get_currencies()
        elif self.path == '/exchange_rates':
            self.handle_get_exchange_rates()
        elif self.path == '/':
            self.handle_html_page()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/currencies':
            self.handle_add_currency()
        elif self.path == '/exchange_rates':
            self.handle_add_exchange_rate()
        elif self.path == '/convert':
            self.handle_convert_currency()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_get_currencies(self):
        currencies = self.model.get_currencies()  # Получаем список словарей [{"code": "USD", "name": "Dollar"}, ...]
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(currencies).encode())  # Преобразуем список словарей в JSON-строку

    def handle_add_currency(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        try:
            self.model.add_currency(data['code'], data['name'])
            self.send_response(201)
        except ValueError as e:
            self.send_response(400)
            self.wfile.write(str(e).encode())
        self.end_headers()

    def handle_get_exchange_rates(self):
        rates = self.model.get_exchange_rates()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(rates).encode())

    def handle_add_exchange_rate(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        try:
            self.model.add_exchange_rate(data['from'], data['to'], data['rate'])
            self.send_response(201)
        except ValueError as e:
            self.send_response(400)
            self.wfile.write(str(e).encode())
        self.end_headers()

    def handle_convert_currency(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        try:
            converted_amount = self.model.convert_currency(data['from'], data['to'], data['amount'])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'converted_amount': converted_amount}).encode())
        except ValueError as e:
            self.send_response(400)
            self.wfile.write(str(e).encode())
        self.end_headers()

    def handle_html_page(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open('index.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
        self.wfile.write(html_content.encode())

def start_server():
    server = HTTPServer(('localhost', 8000), RequestHandler)
    print('Server running on http://localhost:8000')
    server.serve_forever()