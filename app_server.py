import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from router import Router
from viewer import Viewer
import json

logger = logging.getLogger(__name__)


class RequestHandler(BaseHTTPRequestHandler):
    def send_json_response(self, status_code, data):
        logger.debug(f"Отправка JSON-ответа с кодом {status_code}: {data}")
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=4, ensure_ascii=False).encode('utf-8'))

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
        router = Router()
        viewer = Viewer()
        dto = router.handle_request(self)

        # Получаем статус ответа из dto
        status_code = getattr(dto, 'status_code', 200)  # По умолчанию 200, если статус не задан

        if isinstance(dto.response, str):  # Если это HTML-страница
            self.send_response(status_code)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(viewer.render_html(dto.response).encode())
        else:  # Если это JSON-ответ
            self.send_json_response(status_code, viewer.render_json(dto.response))

    def do_POST(self):
        logger.info("Обработка POST-запроса")
        router = Router()
        logger.debug(f"Экземпляр класса Router - {router.__dict__}")
        dto = router.handle_request(self)
        status_code = getattr(dto, 'status_code', 200)  # По умолчанию 200, если статус не задан
        self.send_json_response(status_code, dto.response)

    def do_PATCH(self):
        logger.info("Обработка PATCH-запроса")
        router = Router()
        logger.debug(f"Экземпляр класса Router - {router.__dict__}")
        dto = router.handle_request(self)
        status_code = getattr(dto, 'status_code', 200)  # По умолчанию 200, если статус не задан
        self.send_json_response(status_code, dto.response)

def start_server():
    logger.info("Запуск HTTP-сервера на http://localhost:8000")
    server = HTTPServer(('localhost', 8000), RequestHandler)
    server.serve_forever()