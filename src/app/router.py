
import json
import logging
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from controller import Controller
from errors import APIError, InvalidPairError, RouteNotFoundError

logger = logging.getLogger(__name__)

class Router:
    def __init__(self, db_path: str = None):
        logger.info("Инициализация Router")
        self.static_routes = {}
        self.dynamic_routes = []
        self._register_routes(db_path)

    def _register_routes(self,  db_path: str = None) -> None:
        controller = Controller(db_path)

        # Обработчики контроллера
        get_currency = (controller.get_currency_by_code, ['code'])
        add_currency = (controller.add_currency, ['code', 'name'])
        get_exchange_rate = (controller.get_exchange_rate, ['from', 'to'])
        add_exchange_rate = (controller.add_exchange_rate, ['from', 'to', 'rate'])
        convert_currency = (controller.convert_currency, ['from', 'to', 'amount'])
        get_exchange_rates = (controller.get_exchange_rates, [])
        handle_html = (controller.handle_html_page, [])
        return_icon = (controller.return_icon, [])
        update_exchange_rate = (controller.update_exchange_rate, ['from', 'to', 'rate'])
        delete_all_currencies = (controller.delete_all_currencies, [])

        # Статические маршруты
        self.static_routes[('GET', '/currencies')] = (controller.get_currencies, [])
        self.static_routes[('GET', '/currency')] = get_currency
        self.static_routes[('POST', '/currencies')] = add_currency
        self.static_routes[('GET', '/exchangeRate')] = get_exchange_rate
        self.static_routes[('POST', '/exchangeRates')] = add_exchange_rate
        self.static_routes[('GET', '/exchangeRates')] = get_exchange_rates
        self.static_routes[('GET', '/convert')] = convert_currency
        self.static_routes[('GET', '/favicon.ico')] = return_icon
        self.static_routes[('GET', '/')] = handle_html
        self.static_routes[('PATCH', '/exchangeRate')] = update_exchange_rate
        self.static_routes[('POST', '/currencies/delete_all')] =  delete_all_currencies
        # Динамические маршруты
        self.dynamic_routes.append(('GET', '/currency/:code', get_currency))
        self.dynamic_routes.append(('GET', '/exchangeRate/:pair', get_exchange_rate))
        self.dynamic_routes.append(('PATCH', '/exchangeRate/:pair', update_exchange_rate))

    def handle_request(self, handler: BaseHTTPRequestHandler) -> tuple:
        logger.info(f"Обработка запроса: {handler.command} {handler.path}")
        parsed_path = urlparse(handler.path)
        query_params = {k: v[0] for k, v in parse_qs(parsed_path.query).items()}
        body = self._parse_body(handler)
        url = parsed_path.path
        method = handler.command
        params = {**query_params, **body} # Объединяем параметры запроса и тела запроса в один словарь

        return self._resolve(method, url, params)

    def _resolve(self, method: str, url: str, params: dict) -> tuple:
        logger.debug(f"Маршрутизация запроса: {method} {url}")

        # Проверка на статический маршрут
        route = self.static_routes.get((method, url))
        if route:
            handler_controller, args = route
            func_args = [params.get(arg) for arg in args]
            return self._safe_call(handler_controller, func_args)

        # Проверка на динамические маршруты
        for m, route_pattern, route_info in self.dynamic_routes:
            if m == method and self.match_dynamic_route(route_pattern, url, params):
                handler_controller, args = route_info

                # Разбор пары валют вида /exchangeRate/USDJPY → from=USD, to=JPY
                if 'pair' in params and set(args) >= {'from', 'to'}:
                    pair = params['pair']
                    if isinstance(pair, str) and len(pair) == 6:
                        params['from'] = pair[:3].upper()
                        params['to'] = pair[3:].upper()
                        logger.debug(f"Разобранная пара: from={params['from']}, to={params['to']}")
                    else:
                        logger.warning(f"Некорректный формат pair: '{pair}'")
                        raise InvalidPairError()
                        return
                func_args = [params.get(arg) for arg in args]
                return self._safe_call(handler_controller, func_args)

        logger.warning(f"Маршрут не найден: {method} {url}")
        raise RouteNotFoundError()


    def _safe_call(self, handler_controller: callable, func_args: list) -> tuple:  # Возвращает результат обработчика и статус-код ответа
        try:
            logger.debug(f"Вызов обработчика: {handler_controller.__name__} с аргументами: {func_args}")
            response, code = handler_controller(*func_args) if func_args else handler_controller()
            return response, code
        except APIError as e:
            logger.error(f"API ошибка: {e.message}")
            return e.to_dict(), e.status_code
        except Exception:
            logger.exception("Необработанная ошибка в контроллере")
            return {"error": "Internal Server Error"}, 500

    def match_dynamic_route(self, route : str, url, query_params: dict) -> bool: # Сопоставляет динамический маршрут с текущим URL
        route_parts = route.strip('/').split('/')
        url_parts = url.strip('/').split('/')

        if len(route_parts) != len(url_parts):
            return False

        for route_part, url_part in zip(route_parts, url_parts):
            if route_part.startswith(':'):
                query_params[route_part[1:]] = url_part
            elif route_part != url_part:
                return False

        return True

    def _parse_body(self, handler: BaseHTTPRequestHandler) -> dict  : #Парсит тело запроса в зависимости от типа контента
        logger.info("Парсинг тела запроса")
        content_length = int(handler.headers.get('Content-Length', 0))

        if content_length > 0:
            body_bytes = handler.rfile.read(content_length)
            body = body_bytes.decode('utf-8')
            content_type = handler.headers.get('Content-Type', '').split(';')[0].strip()

            if content_type == 'application/json':
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    logger.error("Ошибка декодирования JSON")
                    return {}
            elif content_type == 'application/x-www-form-urlencoded':
                return {k: v[0] for k, v in parse_qs(body).items()}
            else:
                logger.warning(f"Неподдерживаемый Content-Type: {content_type}")
                return {}

        return {}
