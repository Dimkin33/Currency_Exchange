import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv
from errors import APIError
from router import Router

logger = logging.getLogger(__name__)


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, db_path = None, **kwargs):
        logger.info("Инициализация RequestHandler")
        self.router = Router(db_path)
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

    def do_GET(self):  # noqa: N802
        self.handle_method()

    def do_POST(self):  # noqa: N802
        self.handle_method()

    def do_PATCH(self):  # noqa: N802
        self.handle_method()



def start_server(db_path: str = None) -> None:
    """Запуск HTTP-сервера"""
    logger.info("Запуск сервера")

    # Загрузка переменных окружения
    load_dotenv()
    host = os.getenv('HOST', 'localhost')  # Хост из переменной окружения
    port = int(os.getenv('PORT', 8000))  # Порт из переменной окружения
    logger.info("Запуск HTTP-сервера на %s:%d", host, port)

    # Создание и запуск HTTP-сервера с передачей db_path в RequestHandler через lambda
    server = HTTPServer(
        (host, port),
        lambda *args, **kwargs: RequestHandler(*args, db_path=db_path, **kwargs)  # Передаем db_path в RequestHandler
    )
    server.serve_forever()
