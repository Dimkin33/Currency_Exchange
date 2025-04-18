import logging
from model import CurrencyModel
from sign_code import currency_sign
from dto import currencyDTO, currencyExchangeDTO, requestDTO
from errors import *
logger = logging.getLogger(__name__)

class Controller:
    def __init__(self):
        self.model = CurrencyModel()

    def get_currencies(self, dto):
        logger.info("Получение списка валют")
        try:
            currencies = self.model.get_currencies()
            logger.debug(f"Список валют: {currencies}")
            dto.response = currencies
        except Exception as e:
            logger.error(f"Ошибка при получении списка валют: {e}")
            raise APIError("Failed to retrieve currencies")

    def get_currency_by_code(self, dto):
        logger.info("Получение валюты по коду")
        code = dto.query_params.get('code', [None])
        # if code:
        #     code = code.upper()
        logger.debug(f"Код валюты из запроса: {code}")
        if not code:
            raise MissingCurrencyCodeError()
        try:
            currency = self.model.get_currency_by_code(code)
            logger.info(f"Валюта найдена: {currency}")
            dto.response = currency
            return currency
        except CurrencyNotFoundError as e:
            raise e
        except Exception as e:
            raise APIError("Failed to retrieve currency")

    def get_currency_by_code_dynamic(self, dto):
        logger.info("Получение валюты по коду (динамический метод)")
        code = dto.query_params.get('code')
        logger.debug(f"Код валюты из запроса: {code}")
        if not code:
            raise MissingCurrencyCodeError()
        self.get_currency_by_code(dto)

    def get_exchange_rates_dynamic(self, dto):
        logger.info("Получение пары валют по коду (динамический метод)")
        pair = dto.query_params.get('pair')
        if not pair:
            raise MissingCurrencyCodeError()
        dto.body['from'] = pair[:3].upper()
        dto.body['to'] = pair[3:].upper()
        dto.query_params['from'] = pair[:3].upper()
        dto.query_params['to'] = pair[3:].upper()
        self.get_exchange_rate(dto)

    def add_currency(self, dto):
        logger.info("Добавление новой валюты")
        code = dto.body.get('code')
        if not code:
            raise MissingRequiredFieldsError()
        name, sign = currency_sign[code][0], currency_sign[code][1]
        currency_DTO = currencyDTO(code=code, name=name, sign=sign)
        try:
            self.model.add_currency(currency_DTO.code, currency_DTO.name, currency_DTO.sign)
            dto.response = currency_DTO.to_dict()
        except CurrencyAlreadyExistsError as e:
            raise e
        except Exception as e:
            raise APIError("Failed to add currency")

    def get_exchange_rates(self, dto):
        logger.info("Получение всех курсов обмена валют")
        try:
            rates = self.model.get_exchange_rates()
            logger.debug(f"Курсы обмена: {rates}")
            dto.response = rates
        except Exception as e:
            raise APIError("Failed to retrieve exchange rates")

    def add_exchange_rate(self, dto):
        logger.info("Добавление нового курса обмена")
        from_currency = dto.body.get('from')
        to_currency = dto.body.get('to')
        rate = dto.body.get('rate')

        if not from_currency or not to_currency or not rate:
            raise MissingRequiredFieldsError()

        try:
            base_currency = self.model.get_currency_by_code(from_currency)
            target_currency = self.model.get_currency_by_code(to_currency)
            if not base_currency or not target_currency:
                raise CurrencyNotFoundError(code=f"{from_currency or ''}{to_currency or ''}")

            self.model.add_exchange_rate(from_currency, to_currency, float(rate))
            result = self.model.get_exchange_rate(from_currency, to_currency)
            dto.response = {
                'id': result['id'],
                'baseCurrency': base_currency,
                'targetCurrency': target_currency,
                'rate': result['rate']
            }

        except CurrencyAlreadyExistsError as e:
            raise e
        except Exception as e:
            raise APIError("Failed to add exchange rate")

    def get_exchange_rate(self, dto):
        logger.info("Просмотр курса обмена")
        from_currency = dto.query_params.get('from')
        to_currency = dto.query_params.get('to')
        if not from_currency or not to_currency:
            raise MissingRequiredFieldsError()
        try:
            result = self.model.get_exchange_rate(from_currency, to_currency)
            if result:
                dto.response = {
                    'id': result['id'],
                    'baseCurrency': self.model.get_currency_by_code(from_currency),
                    'targetCurrency': self.model.get_currency_by_code(to_currency),
                    'rate': result['rate']
                }
            else:
                raise ExchangeRateNotFoundError(from_currency=from_currency, to_currency=to_currency)
        except Exception as e:
            raise APIError("Failed to retrieve exchange rate")

    def update_exchange_rate(self, dto):
        logger.info("Обновление курса обмена")
        from_currency = dto.body.get('from')
        to_currency = dto.body.get('to')
        rate = dto.body.get('rate')
        if not from_currency or not to_currency:
            raise MissingRequiredFieldsError()
        try:
            self.model.patch_exchange_rate(from_currency, to_currency, float(rate))
            result = self.model.get_exchange_rate(from_currency, to_currency)
            dto.response = {
                'id': result['id'],
                'baseCurrency': self.model.get_currency_by_code(from_currency),
                'targetCurrency': self.model.get_currency_by_code(to_currency),
                'rate': result['rate']
            }
        except ExchangeRateNotFoundError as e:
            raise e
        except Exception as e:
            raise APIError("Failed to update exchange rate")

    def update_exchange_rate_by_pair(self, dto):
        logger.info("Обновление курса обмена по валютной паре")
        pair = dto.query_params.get('pair')
        rate = dto.body.get('rate')

        if not pair or not rate:
            raise MissingRequiredFieldsError()

        try:
            from_currency, to_currency = pair[:3], pair[3:]
            self.model.patch_exchange_rate(from_currency, to_currency, float(rate))
            self.get_exchange_rate(dto)
        except ExchangeRateNotFoundError as e:
            raise e
        except Exception as e:
            raise APIError("Failed to update exchange rate")

    def convert_currency(self, dto):
        logger.info("Конвертация валюты")
        from_currency = dto.query_params.get('from', [None])[0]
        to_currency = dto.query_params.get('to', [None])[0]
        amount = dto.query_params.get('amount', [None])[0]
        if not from_currency or not to_currency or not amount:
            raise MissingRequiredFieldsError()
        try:
            amount = float(amount)
            converted_amount = self.model.convert_currency(from_currency, to_currency, amount)
            dto.response = {
                "from": from_currency,
                "to": to_currency,
                "amount": amount,
                "converted_amount": converted_amount
            }
        except Exception as e:
            raise APIError("Failed to convert currency")

    def handle_html_page(self, dto):
        logger.info("Обработка HTML-страницы")
        try:
            with open('index.html', 'r', encoding='utf-8') as file:
                dto.response = file.read()
        except FileNotFoundError:
            raise APIError("HTML file not found")
