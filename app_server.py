from dotenv import load_dotenv
import os

import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from router import Router
import sqlite3
from errors import APIError
import json

logger = logging.getLogger(__name__)


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Загрузка переменных окружения
        load_dotenv()
        db_path = os.getenv('DB_PATH', 'currency.db')  # Путь к базе данных из переменной окружения
        connector = sqlite3.connect(db_path, uri=True)  # Подключение к базе данных
        self.router = Router(connector)

        logger.info("Инициализация RequestHandler")
        super().__init__(*args, **kwargs)

    def send_response_content(self, status_code : int, data : any, content_type : str = None) -> None:# функция отправки ответа на запрос

        if isinstance(data, dict) or isinstance(data, list):
            response_body = json.dumps(data, indent=4, ensure_ascii=False)
            content_type = content_type or 'application/json; charset=utf-8'
        elif isinstance(data, str):
            response_body = data
            content_type = content_type or 'text/html; charset=utf-8'
        else:
            response_body = str(data)
            content_type = content_type or 'text/plain; charset=utf-8'

        logger.debug(f"Отправка ответа c кодом состояния: {status_code}: с типом: {content_type}, тип содержимого: {type(data).__name__}")
        self.send_response(status_code) # устанавливаем код состояния ответа
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(response_body.encode('utf-8'))


    def handle_method(self) -> None:
        logger.info(f"Обработка {self.command}-запроса")
        try:
            result, status_code = self.router.handle_request(self)
            self.send_response_content(status_code, result)
        except APIError as e:
            logger.warning(f"APIError: {e.message}")
            self.send_response_content(e.status_code, e.to_dict())
        except Exception:
            logger.exception("Неизвестная ошибка")
            self.send_response_content(500, {"error": "Internal Server Error"})

    def do_GET(self):
        self.handle_method()

    def do_POST(self):
        self.handle_method()

    def do_PATCH(self):
        self.handle_method()



def start_server():
    logger.info("Запуск HTTP-сервера на http://localhost:8000")
    server = HTTPServer(('localhost', 8000), RequestHandler)
    server.serve_forever()
