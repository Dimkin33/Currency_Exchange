import logging
import json
from urllib.parse import urlparse, parse_qs
from controller import Controller
from dto import requestDTO
from errors import APIError

logger = logging.getLogger(__name__)

class Router:
    def __init__(self):
        logger.info("Инициализация Router")
        self.static_routes = {}
        self.dynamic_routes = []
        self._register_routes()

    def _register_routes(self):
        controller = Controller()

        # Статические маршруты
        self.static_routes[('GET', '/currencies')] = controller.get_currencies
        self.static_routes[('GET', '/currency')] = controller.get_currency_by_code
        self.static_routes[('GET', '/exchangeRates')] = controller.get_exchange_rates
        self.static_routes[('POST', '/currencies')] = controller.add_currency
        self.static_routes[('POST', '/exchangeRates')] = controller.add_exchange_rate
        self.static_routes[('GET', '/exchangeRate')] = controller.get_exchange_rate
        self.static_routes[('GET', '/convert')] = controller.convert_currency
        self.static_routes[('GET', '/')] = controller.handle_html_page
        self.static_routes[('PATCH', '/exchangeRate')] = controller.update_exchange_rate

        # Динамические маршруты
        self.dynamic_routes.append(('GET', '/currency/:code', controller.get_currency_by_code_dynamic))
        self.dynamic_routes.append(('GET', '/exchangeRates/:pair', controller.get_exchange_rates_dynamic))
        self.dynamic_routes.append(('PATCH', '/exchangeRate/:pair', controller.update_exchange_rate_by_pair))

        logger.debug(f"Статические маршруты: {self.static_routes.keys()}")
        logger.debug(f"Динамические маршруты: {[r[1] for r in self.dynamic_routes]}")

    def resolve(self, dto):
        logger.debug(f"Маршрутизация запроса: {dto.method} {dto.url}")

        handler = self.static_routes.get((dto.method, dto.url))
        if handler:
            logger.info(f"Найден статический маршрут: {dto.method} {dto.url}")
            return self._safe_call(handler, dto)

        for method, route, route_handler in self.dynamic_routes:
            if method == dto.method and self.match_dynamic_route(route, dto.url, dto):
                logger.info(f"Найден динамический маршрут: {dto.method} {dto.url}")
                return self._safe_call(route_handler, dto)

        logger.warning(f"Маршрут не найден: {dto.method} {dto.url}")
        dto.response = {"error": "Route not found"}
        dto.status_code = 404
        logger.debug(f"Статус код: {dto.status_code}")
        return dto

    def _safe_call(self, handler, dto):
        try:
            handler(dto)
            logger.debug(f"Обработчик {handler.__name__} завершил выполнение без ошибок")
        except APIError as e:
            logger.error(f"API ошибка: {e.message}")
            dto.response = e.to_dict()
            dto.status_code = e.status_code
        except Exception as e:
            logger.exception("Необработанная ошибка в контроллере")
            dto.response = {"error": "Internal server error"}
            dto.status_code = 500

        

    def match_dynamic_route(self, route, url, dto):
        logger.debug(f"Сопоставление динамического маршрута: {route} с {url}")
        dto.query_params = {}
        route_parts = route.split('/')
        url_parts = url.split('/')

        if len(route_parts) != len(url_parts):
            logger.debug("Длина частей маршрута и URL не совпадает")
            return False

        for route_part, url_part in zip(route_parts, url_parts):
            if route_part.startswith(':'):
                param_name = route_part[1:]
                dto.query_params[param_name] = url_part
                logger.debug(f"Динамический параметр: {param_name} = {url_part}")
            elif route_part != url_part:
                logger.debug(f"Статическая часть не совпадает: {route_part} != {url_part}")
                return False

        logger.info(f"Динамический маршрут успешно сопоставлен: {route} с {url}")
        return True

    def handle_request(self, handler):
        logger.info(f"Обработка запроса:  {handler.command} {handler.path}")
        parsed_path = urlparse(handler.path)
        logger.debug(f"Парсинг пути запроса: {parsed_path}")
        query_params = {k: v[0] for k, v in parse_qs(parsed_path.query).items()}

        logger.debug(f"Путь запроса: {parsed_path.path}, параметры: {query_params}")

        dto = requestDTO(
            method=handler.command,
            url=parsed_path.path,
            body=self._parse_body(handler),)
        
        dto.query_params = query_params

        logger.debug(f"DTO создан: {dto}")
        self.resolve(dto)
        if not hasattr(dto, 'status_code'):
            logger.warning("status_code не установлен, используется значение по умолчанию 500")
            dto.status_code = 500

        #dto.status_code = 200
        logger.debug(f"Ответ DTO: {dto.response} {dto.status_code}")
        return dto

    def _parse_body(self, handler):
        logger.info("Парсинг тела запроса")
        content_length = int(handler.headers.get('Content-Length', 0))
        if content_length > 0:
            body = handler.rfile.read(content_length).decode('utf-8')
            logger.debug(f"Тело запроса (сырое): {body}")
            content_type = handler.headers.get('Content-Type', '')

            if content_type == 'application/json':
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    logger.error("Ошибка декодирования JSON")
                    return {"error": "Invalid JSON"}

            elif content_type == 'application/x-www-form-urlencoded':
                return {k: v[0] for k, v in parse_qs(body).items()}

            else:
                logger.warning("Неизвестный Content-Type")
                return {"error": "Unsupported Content-Type"}

        logger.debug("Тело запроса пустое")
        return {}
