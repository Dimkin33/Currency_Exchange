from router import Router
from urllib.parse import urlparse, parse_qs
from dto import requestDTO
import logging

logger = logging.getLogger(__name__)

# Viewer теперь отвечает только за отображение данных.
class Viewer:
    def render_html(self, html_content):
        logger.info("Рендеринг HTML-страницы")
        return html_content

    def render_json(self, data):
        logger.info("Рендеринг JSON-ответа")
        return data
