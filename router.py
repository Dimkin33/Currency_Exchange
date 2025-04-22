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

        # Обработчики контроллера
        get_currency = (controller.get_currency_by_code, ['code'])
        add_currency = (controller.add_currency, ['code'])
        get_exchange_rate = (controller.get_exchange_rate, ['from', 'to'])
        add_exchange_rate = (controller.add_exchange_rate, ['from', 'to', 'rate'])
        convert_currency = (controller.convert_currency, ['from', 'to', 'amount'])
        get_exchange_rates = (controller.get_exchange_rates, [])
        handle_html = (controller.handle_html_page, [])
        update_exchange_rate = (controller.update_exchange_rate, ['from', 'to', 'rate'])

        # Статические маршруты
        self.static_routes[('GET', '/currencies')] = (controller.get_currencies, [])
        self.static_routes[('GET', '/currency')] = get_currency
        self.static_routes[('POST', '/currencies')] = add_currency
        self.static_routes[('GET', '/exchangeRate')] = get_exchange_rate
        self.static_routes[('POST', '/exchangeRates')] = add_exchange_rate
        self.static_routes[('GET', '/exchangeRates')] = get_exchange_rates
        self.static_routes[('GET', '/convert')] = convert_currency
        self.static_routes[('GET', '/')] = handle_html
        self.static_routes[('PATCH', '/exchangeRate')] = update_exchange_rate

        # Динамические маршруты → используют те же обработчики, что и статические
        self.dynamic_routes.append(('GET', '/currency/:code', get_currency))
        self.dynamic_routes.append(('GET', '/exchangeRate/:pair', get_exchange_rate))  # pair будет парситься в from/to заранее
        self.dynamic_routes.append(('PATCH', '/exchangeRate/:pair', update_exchange_rate))




        logger.debug(f"Статические маршруты: {self.static_routes.keys()}")
        logger.debug(f"Динамические маршруты: {[r[1] for r in self.dynamic_routes]}")

    def resolve(self, dto: requestDTO) -> (str, int): # Маршрутизация запроса Возвращает ответ и статус код
        logger.debug(f"Маршрутизация запроса: {dto.method} {dto.url}")

        route = self.static_routes.get((dto.method, dto.url))
        if route:
            logger.info(f"Найден статический маршрут: {dto.method} {dto.url}")
            handler, args = route
            return self._safe_call(handler, dto, args)

        for method, route, route_info in self.dynamic_routes:
            if method == dto.method and self.match_dynamic_route(route, dto.url, dto):
                logger.info(f"Найден динамический маршрут: {dto.method} {dto.url}")
                handler, args = route_info
                logger.debug(f"Динамический маршрут: {route} с параметрами: {handler.__name__}, {args}, {dto.query_params}")

                # Разбор pair → from / to, если нужно
                if 'pair' in dto.query_params and set(args) >= {'from', 'to'}:
                    pair = dto.query_params['pair']
                    if isinstance(pair, str) and len(pair) == 6:
                        dto.body['from'] = pair[:3].upper()
                        dto.body['to'] = pair[3:].upper()
                        logger.debug(f"Разобранная пара: from={dto.body['from']}, to={dto.body['to']}")
                    else:
                        logger.warning(f"Некорректный формат pair: '{pair}'")

                return self._safe_call(handler, dto, args)


        logger.warning(f"Маршрут не найден: {dto.method} {dto.url}")
        raise RouteNotFoundError()
        return dto 


    def _safe_call(self, handler, dto: requestDTO, args: list) -> requestDTO:
        try:
            logger.debug(f"Все параметры: {dto.query_params | dto.body}")
            logger.debug(f"Вызов обработчика: {handler.__name__}, аргументы: {args}")
            handler(dto)
            dto.status_code = dto.status_code or 200
        except APIError as e:
            logger.error(f"API ошибка: {e.message}")
            dto.response = e.to_dict()
            dto.status_code = e.status_code
        except Exception as e:
            logger.exception("Необработанная ошибка в контроллере")
            raise APIError()
        return (dto.response, dto.status_code)

        

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
        body=self._parse_body(handler)
        logger.debug(f"Путь запроса: {parsed_path.path}, параметры: {query_params}, тело: {body}")

        dto = requestDTO(
            method=handler.command,
            url=parsed_path.path,
            body= body,
            query_params = query_params,)
        
        logger.debug(f"DTO создан: {dto}")

        return self.resolve(dto) # Сопоставление запроса с маршрутом и вызов обработчика Возвращает ответ и статус код

    def _parse_body(self, handler):
        logger.info("Парсинг тела запроса")
        content_length = int(handler.headers.get('Content-Length', 0))

        if content_length > 0:
            body_bytes = handler.rfile.read(content_length)
            body = body_bytes.decode('utf-8')
            content_type = handler.headers.get('Content-Type', '').split(';')[0].strip()

            logger.debug(f"Тело запроса (сырое): {body}, тип: {type(body)}, content-type: {content_type}")

            if content_type == 'application/json':
                try:
                    parsed = json.loads(body)
                    logger.debug(f"JSON тело запроса (обработанное): {parsed}")
                    return parsed
                except json.JSONDecodeError:
                    logger.error("Ошибка декодирования JSON")
                    return {"error": "Invalid JSON"}

            elif content_type == 'application/x-www-form-urlencoded':
                parsed = {k: v[0] for k, v in parse_qs(body).items()}
                logger.debug(f"Form тело запроса (обработанное): {parsed}")
                return parsed

            else:
                logger.warning(f"Неподдерживаемый Content-Type: {content_type}")
                return {"error": "Unsupported Content-Type"}

        logger.debug("Тело запроса пустое")
        return {}

