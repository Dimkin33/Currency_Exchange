from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from model import CurrencyModel
import os
from urllib.parse import urlparse, parse_qs
from viewer import Viewer
from dto import requestDTO
from router import Router


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.model = CurrencyModel()
        super().__init__(*args, **kwargs)

    def transfer_object(self, obj):
        return json.dumps(obj, indent=4, ensure_ascii=False).encode('utf-8')
    
    def send_json_response(self, status_code, data):
        """Отправляет форматированный JSON-ответ с указанным статусом и данными."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')  # Указана кодировка UTF-8
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=4, ensure_ascii=False).encode('utf-8'))  # Указана кодировка и ensure_ascii=False

    def parse_json_request(self):
        """Читает и парсит JSON из тела запроса."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        return json.loads(post_data)

    def request_to_DTO(self):
        """Создает объект DTO из запроса."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        method = self.command
        url = self.path
        headers = dict(self.headers) # Получаем объект Router и вызываем метод resolve
        return  requestDTO(method, url, headers, body)  # Возвращаем объект DTO с методом, URL и заголовками запроса
    
    def do_GET(self):
        print('do_GET method called')
        request_ = self.request_to_DTO()
        #request_.controller 
        # Получаем объект Router и вызываем метод resolve
        Router(request_).resolve()
        print(request_.controller)
        request_.controller(self)
        
        
        # parsed_path = urlparse(self.path)
        # query_params = parse_qs(parsed_path.query)
        # print(f'get query_params =  {query_params},  path = {parsed_path.path}')
        
        # if self.path.startswith('/convert?'):  # Проверяем, начинается ли путь с /convert?
        #     self.convert_currency_get()  # Обработчик для GET-запроса на конвертацию валют
        # elif self.path.startswith('/exchangeRates'):  # Проверяем, начинается ли путь с /exchangeRate/
        #     self.get_exchange_rates(query_params, parsed_path.path)  # Обработчик для получения обменных курсов)  # Обработчик для получения конкретного обменного курса
        # elif self.path.startswith('/currency'):  # Проверяем, начинается ли путь с /currency/
        #     self.get_currency_by_code(query_params.get('code', [''])[0])  # Обработчик для получения конкретной валюты
        # elif self.path == '/currencies?':
            
        #     self.get_currencies()
        # elif self.path.startswith('/exchangeRate/'):
        #     self.get_exchange_rate(parsed_path.path)
        # #elif self.path == '/':
        #     #self.handle_html_page()
        # else:
        #     self.send_response(404)
        #     self.end_headers()

    def do_POST(self):
        print('do_POST method called')
        res = self.request_to_DTO()
        print(f'request_DTO = {res.to_dict()}')
          

        post_data = res.body
        form_data = dict(x.split('=') for x in post_data.split('&'))
        

        
        
        if self.path == '/currencies':  
            self.add_currency(form_data)
        elif self.path == '/exchangeRates':
            self.add_exchange_rate(form_data)
   
        elif self.path == '/convert':
            self.convert_currency()
        else:
            self.send_response(404)
            self.end_headers()
            
    def get_currency_by_code(self, code):
        if not code:
            code = self.path.split('/')[-1]
        currency = self.model.get_currency_by_code(code)
        if currency:        
            self.send_json_response(200, currency)
        else:
            self.send_json_response(404, {'error': 'Currency not found'})
            

    def add_currency(self, form_data):
        try:
            # content_length = int(self.headers['Content-Length'])
            # post_data = self.rfile.read(content_length).decode('utf-8')
            # form_data = dict(x.split('=') for x in post_data.split('&'))

            name = form_data.get('name')
            code = form_data.get('code')
            sign = form_data.get('sign')

            if not code:
                self.send_json_response(400, {'error': 'Missing required fields:  code'})
                return

            try:
                self.model.add_currency(code, name, sign)
                self.send_json_response(201, self.model.get_currency_by_code(code))
            except ValueError:
                self.send_json_response(409, {'error': 'Currency with this code already exists'})
        except Exception as e:
            self.send_json_response(500, {'error': 'Internal server error', 'details': str(e)})

    def get_currencies(self):
        currencies = self.model.get_currencies()  # Получаем список словарей
        self.send_json_response(200, currencies)  # Используем send_json_response

    def get_exchange_rates(self, query_params, path):
        if 'from' in query_params and 'to' in query_params:
            from_currency = query_params['from'][0]
            to_currency = query_params['to'][0]
            exchange_rate = self.model.get_exchange_rate(to_currency, from_currency)
            if exchange_rate:
                self.send_json_response(200, exchange_rate)
        else:
            if path == '/exchangeRates':
                rates = self.model.get_exchange_rates()
                self.send_json_response(200, rates)
            else:
                print(path.split('/')[-1])# Используем send_json_response

    def get_exchange_rate(self, path):
        from_currency = path.split('/')[-1][:3]
        to_currency = path.split('/')[-1][3:]
        exchange_rate = self.model.get_exchange_rate(from_currency, to_currency)
        if exchange_rate:
            base_currency = self.model.get_currency_by_code(from_currency)
            target_currency = self.model.get_currency_by_code(to_currency)
            if base_currency and target_currency:
                self.send_json_response(201, {
                    'id': exchange_rate['id'],  # ID можно заменить на реальный, если он есть в базе данных
                    'baseCurrency': {
                        'id': base_currency['id'],  # ID можно заменить на реальный,  # ID можно заменить на реальный
                        'name': base_currency['name'],
                        'code': base_currency['code'],
                        'sign': base_currency.get('sign', '')
                    },
                    'targetCurrency': {
                        'id': target_currency['id'],  # ID можно заменить на реальный
                        'name': target_currency['name'],
                        'code': target_currency['code'],
                        'sign': target_currency.get('sign', '')
                    },
                    'rate': float(exchange_rate['rate'])
                })
            else:
                self.send_json_response(400, {'error': 'Currency not found'})
        else:
            self.send_json_response(404, {'error': 'Exchange rate not found'})

    def add_exchange_rate(self, data):

        try:
            if not all(key in data for key in ['from', 'to', 'rate']):
                self.send_json_response(400, {'error': 'Missing required fields: from, to, rate'})
                return  

            base_currency = self.model.get_currency_by_code(data['from'])
            target_currency = self.model.get_currency_by_code(data['to'])
            exchange_rate = self.model.get_exchange_rate(data['to'], data['from'])
            self.model.add_exchange_rate(data['from'], data['to'], data['rate'])
            exchange_rate = self.model.get_exchange_rate(data['to'], data['from'])         
            
            self.send_json_response(201, {
                'id': exchange_rate['id'],  
                'baseCurrency': {
                    'id': base_currency['id'],  
                    'name': base_currency['name'],
                    'code': base_currency['code'],
                    'sign': base_currency.get('sign', '')
                },
                'targetCurrency': {
                    'id': target_currency['id'],  
                    'name': target_currency['name'],
                    'code': target_currency['code'],
                    'sign': target_currency.get('sign', '')
                },
                'rate': float(data['rate'])
            })
        except ValueError as e:
            self.send_json_response(400, {'error': str(e)})

    def convert_currency(self):
        try:
            data = self.parse_json_request()  # Используем новую функцию
            amount = float(data['amount'])
            converted_amount = self.model.convert_currency(data['from'], data['to'], amount)
            self.send_json_response(200, {'converted_amount': converted_amount})
        except ValueError as e:
            self.send_json_response(400, {'error': str(e)})
        except Exception as e:
            self.send_json_response(500, {'error': 'Internal server error', 'details': str(e)})

    def handle_html_page(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open('index.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
        self.wfile.write(html_content.encode())

    def convert_currency_get(self):
        query_components = parse_qs(urlparse(self.path).query)
        from_currency = query_components.get('from', [None])[0]
        to_currency = query_components.get('to', [None])[0]
        amount = query_components.get('amount', [None])[0]

        if not from_currency or not to_currency or not amount:
            self.send_json_response(400, {'error': 'Missing required parameters'})
            return

        try:
            amount = float(amount)
            converted_amount = self.model.convert_currency(from_currency, to_currency, amount)
            self.send_json_response(200, {'converted_amount': converted_amount})
        except ValueError as e:
            self.send_json_response(400, {'error': str(e)})
        except Exception as e:
            self.send_json_response(500, {'error': 'Internal server error', 'details': str(e)})

def start_server():
    server = HTTPServer(('localhost', 8000), RequestHandler)
    print('Server running on http://localhost:8000')
    server.serve_forever()