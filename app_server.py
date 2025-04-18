import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from router import Router
from viewer import Viewer
from errors import APIError
import json

logger = logging.getLogger(__name__)


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.router = Router()
        self.viewer = Viewer()
        logger.info("Инициализация RequestHandler")
        super().__init__(*args, **kwargs)

    def send_response_content(self, status_code, data, content_type=None):
        if status_code is None:
            logger.warning("status_code не указан, используется 200")
            status_code = 200

        if isinstance(data, dict) or isinstance(data, list):
            response_body = json.dumps(data, indent=4, ensure_ascii=False)
            content_type = content_type or 'application/json; charset=utf-8'
        elif isinstance(data, str):
            response_body = data
            content_type = content_type or 'text/html; charset=utf-8'
        else:
            response_body = str(data)
            content_type = content_type or 'text/plain; charset=utf-8'

        logger.debug(f"Отправка ответа [{status_code}] с типом: {content_type}, тип содержимого: {type(data)}")
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.end_headers()
        self.wfile.write(response_body.encode('utf-8'))


    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/x-icon')
            self.end_headers()
            try:
                with open('favicon.ico', 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
            return

        logger.info("Обработка GET-запроса")

        try:
            dto = self.router.handle_request(self)
            status_code = dto.status_code or 200
            self.send_response_content(status_code, dto.response)
        except APIError as e:
            logger.warning(f"APIError: {e.message}")
            self.send_response_content(e.status_code, e.to_dict())
        except Exception as e:
            logger.exception("Неизвестная ошибка")
            self.send_response_content(500, {"error": "Internal Server Error"})

    def do_POST(self):
        logger.info("Обработка POST-запроса")
        try:
            dto = self.router.handle_request(self)
            status_code = dto.status_code or 200
            self.send_response_content(status_code, dto.response)
        except APIError as e:
            logger.warning(f"APIError: {e.message}")
            self.send_response_content(e.status_code, e.to_dict())
        except Exception as e:
            logger.exception("Неизвестная ошибка")
            self.send_response_content(500, {"error": "Internal Server Error"})

    def do_PATCH(self):
        logger.info("Обработка PATCH-запроса")
        try:
            dto = self.router.handle_request(self)
            status_code = dto.status_code or 200
            self.send_response_content(status_code, dto.response)
        except APIError as e:
            logger.warning(f"APIError: {e.message}")
            self.send_response_content(e.status_code, e.to_dict())
        except Exception as e:
            logger.exception("Неизвестная ошибка")
            self.send_response_content(500, {"error": "Internal Server Error"})


def start_server():
    logger.info("Запуск HTTP-сервера на http://localhost:8000")
    server = HTTPServer(('localhost', 8000), RequestHandler)
    server.serve_forever()
