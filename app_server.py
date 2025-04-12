from http.server import BaseHTTPRequestHandler, HTTPServer
from viewer import Viewer
import json

class RequestHandler(BaseHTTPRequestHandler):
    def send_json_response(self, status_code, data):
        """Отправляет форматированный JSON-ответ с указанным статусом и данными."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=4, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        """Обрабатывает GET-запросы."""
        viewer = Viewer()
        response = viewer.handle_request(self)
        if isinstance(response, str):  # Если это HTML-страница
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode())
        else:  # Если это JSON-ответ
            self.send_json_response(200, response)

    def do_POST(self):
        """Обрабатывает POST-запросы."""
        viewer = Viewer()
        response = viewer.handle_request(self)
        self.send_json_response(200, response)


def start_server():
    """Запускает HTTP-сервер."""
    server = HTTPServer(('localhost', 8000), RequestHandler)
    print('Server running on http://localhost:8000')
    server.serve_forever()