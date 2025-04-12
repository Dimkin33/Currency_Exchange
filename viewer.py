from router import Router
from urllib.parse import urlparse, parse_qs
from dto import requestDTO

class Viewer:
    def handle_request(self, handler):
        parsed_path = urlparse(handler.path)
        query_params = parse_qs(parsed_path.query)
        dto = requestDTO(
            method=handler.command,
            url=parsed_path.path,
            headers=dict(handler.headers),
            body=self._parse_body(handler) if handler.command == 'POST' else {},
        )
        dto.query_params = query_params
        router = Router()
        router.resolve(dto)
        return dto.response

    def _parse_body(self, handler):
        content_length = int(handler.headers.get('Content-Length', 0))
        if content_length > 0:
            body = handler.rfile.read(content_length).decode('utf-8')
            return dict(x.split('=') for x in body.split('&'))
        return {}
