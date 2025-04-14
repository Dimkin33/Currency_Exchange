import logging
from controller import Controller
import json

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
            ('GET', '/exchangeRate'): Controller().get_exchange_rate,
            ('GET', '/convert'): Controller().convert_currency,
            ('GET', '/'): Controller().handle_html_page,
            ('GET', '/currency/:code'): Controller().get_currency_by_code_dynamic,  # Динамический маршрут
            ("GET", "/exchangeRates/:pair") : Controller().get_exchange_rates_dynamic,
            ('PATCH', '/exchangeRate') : Controller().update_exchange_rate,
            ('PATCH', '/exchangeRate/:pair'): Controller().update_exchange_rate_by_pair,
        }
        logger.debug(f"Список маршрутов: {self.routes.keys()}")

    def resolve(self, dto):
        logger.debug(f"Маршрутизация запроса: {dto.method} {dto.url}")
        """
        Определяет маршрут и вызывает соответствующий метод контроллера.
        """
        # Проверяем точное совпадение маршрута
        handler = self.routes.get((dto.method, dto.url), None)
        logger.debug(f"обработчик: {handler}")
        logger.debug(f"Обработчик для маршрута {dto.method} {dto.url}: {handler.__name__ if handler else None}")
        if handler:
            logger.info(f"Маршрут найден: {dto.method} {dto.url}")
            handler(dto)
            return

        # Проверяем динамические маршруты
        for (method, route), route_handler in self.routes.items():
            if method == dto.method and self.match_dynamic_route(route, dto.url, dto):
                logger.info(f"Динамический маршрут найден: {dto.method} {dto.url}")
                route_handler(dto)
                return

        # Если маршрут не найден
        logger.warning(f"Маршрут не найден: {dto.method} {dto.url}")
        dto.response = {"error": "Route not found"}

    def match_dynamic_route(self, route, url, dto):
        """
        Сопоставляет динамический маршрут с URL.
        """
        logger.debug(f"Сопоставление динамического маршрута: {route} с {url}")
        route_parts = route.split('/')
        url_parts = url.split('/')

        if len(route_parts) != len(url_parts):
            logger.debug("Длина частей маршрута и URL не совпадает")
            return False

        for route_part, url_part in zip(route_parts, url_parts):
            if route_part.startswith(':'):  # Это динамическая часть
                param_name = route_part[1:]  # Убираем двоеточие
                dto.query_params[param_name] = url_part
                logger.debug(f"Динамический параметр: {param_name} = {url_part}")
            elif route_part != url_part:  # Это статическая часть
                logger.debug(f"Статическая часть не совпадает: {route_part} != {url_part}")
                return False

        logger.info(f"Динамический маршрут успешно сопоставлен: {route} с {url}")
        return True

    def handle_request(self, handler):
        """
        Обрабатывает запрос и передает его в соответствующий маршрут.
        """
        logger.info(f"Обработка запроса: {handler.command} {handler.path}")
        from dto import requestDTO
        from urllib.parse import urlparse, parse_qs

        # Парсим путь и параметры запроса
        parsed_path = urlparse(handler.path)
        query_params = {k: v[0] for k, v in parse_qs(parsed_path.query).items()}

        logger.debug(f"Путь запроса: {parsed_path.path}, параметры: {query_params}")

        # Создаем DTO из запроса
        dto = requestDTO(
            method=handler.command,
            url=parsed_path.path,
            headers=dict(handler.headers),
            body=self._parse_body(handler),
        )
        dto.query_params = query_params
        logger.debug(f"DTO создан: {dto}")

        # Передаем DTO в маршрутизатор
        self.resolve(dto)

        # Возвращаем ответ
        logger.debug(f"Ответ DTO: {dto.response}")
        return dto

    def _parse_body(self, handler):
        """
        Парсит тело запроса для POST и PATCH-запросов.
        """
        logger.info("Парсинг тела запроса")
        content_length = int(handler.headers.get('Content-Length', 0))
        if content_length > 0:
            body = handler.rfile.read(content_length).decode('utf-8')
            logger.debug(f"Тело запроса (сырое): {body}")

            # Если заголовок Content-Type указывает на JSON
            if handler.headers.get('Content-Type') == 'application/json':
                try:
                    parsed_body = json.loads(body)
                    logger.debug(f"Тело запроса (JSON): {parsed_body}")
                    return parsed_body
                except json.JSONDecodeError:
                    logger.error("Ошибка декодирования JSON")
                    return {"error": "Invalid JSON"}

            # Если Content-Type указывает на form-urlencoded
            elif handler.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
                parsed_body = dict(x.split('=') for x in body.split('&'))
                logger.debug(f"Тело запроса (form-urlencoded): {parsed_body}")
                return parsed_body

            # Если Content-Type неизвестен
            else:
                logger.warning("Неизвестный Content-Type")
                return {"error": "Unsupported Content-Type"}

        logger.debug("Тело запроса пустое")
        return {}


