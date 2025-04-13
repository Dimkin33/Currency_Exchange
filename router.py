import logging
from controller import Controller
logger = logging.getLogger(__name__)



class Router:
    def __init__(self):
        logger.info("Инициализация Router")
        self.routes = {
            ('GET', '/currencies'): Controller().get_currencies,
            ('GET', '/currency'): Controller().get_currency_by_code,
            ('GET', '/exchangeRates'): Controller().get_exchange_rates,
            ('POST', '/currencies'): Controller().add_currency,
            ('POST', '/exchangeRates'): Controller().add_exchange_rate,
            ('GET', '/convert'): Controller().convert_currency,
            ('GET', '/'): Controller().handle_html_page,
            ('GET', '/currency/:code'): Controller().get_currency_by_code_dynamic,  # Динамический маршрут
        }

    def resolve(self, dto):
        logger.debug(f"Маршрутизация запроса: {dto.method} {dto.url}")
        """
        Определяет маршрут и вызывает соответствующий метод контроллера.
        """
        # Проверяем точное совпадение маршрута
        handler = self.routes.get((dto.method, dto.url), None)
        logger.debug(f"Обработчик для маршрута {dto.method} {dto.url}: {handler.__name__ if handler else None}")
        if handler:
            handler(dto)
            return

        # Проверяем динамические маршруты
        for (method, route), route_handler in self.routes.items():
            if method == dto.method and self.match_dynamic_route(route, dto.url, dto):
                route_handler(dto)
                return

        # Если маршрут не найден
        dto.response = {"error": "Route not found"}

    def match_dynamic_route(self, route, url, dto):
        """
        Сопоставляет динамический маршрут с URL.
        """
        route_parts = route.split('/')
        url_parts = url.split('/')

        if len(route_parts) != len(url_parts):
            return False

        for route_part, url_part in zip(route_parts, url_parts):
            if route_part.startswith(':'):  # Это динамическая часть
                param_name = route_part[1:]  # Убираем двоеточие
                dto.query_params[param_name] = url_part
            elif route_part != url_part:  # Это статическая часть
                return False

        return True

    def handle_request(self, handler):
        """
        Обрабатывает запрос и передает его в соответствующий маршрут.
        """
        from dto import requestDTO
        from urllib.parse import urlparse, parse_qs

        # Парсим путь и параметры запроса
        parsed_path = urlparse(handler.path)
        query_params = parse_qs(parsed_path.query)

        # Создаем DTO из запроса
        dto = requestDTO(
            method=handler.command,
            url=parsed_path.path,
            headers=dict(handler.headers),
            body=self._parse_body(handler) if handler.command == 'POST' else {},
        )
        dto.query_params = query_params

        # Передаем DTO в маршрутизатор
        self.resolve(dto)

        # Возвращаем ответ
        return dto.response

    def _parse_body(self, handler):
        """
        Парсит тело запроса для POST-запросов.
        """
        content_length = int(handler.headers.get('Content-Length', 0))
        if (content_length > 0):
            body = handler.rfile.read(content_length).decode('utf-8')
            return dict(x.split('=') for x in body.split('&'))
        return {}


