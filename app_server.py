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
        response = router.handle_request(self)
        if isinstance(response, str):  # Если это HTML-страница
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(viewer.render_html(response).encode())
        else:  # Если это JSON-ответ
            self.send_json_response(200, viewer.render_json(response))

    def do_POST(self):
        logger.info("Обработка POST-запроса")
        router = Router()
        response = router.handle_request(self)
        self.send_json_response(200, response)

def start_server():
    logger.info("Запуск HTTP-сервера на http://localhost:8000")
    server = HTTPServer(('localhost', 8000), RequestHandler)
    server.serve_forever()