import logging
from model import CurrencyModel
from sign_code import currency_sign
from dto import currencyDTO, currencyExchangeDTO, requestDTO
from errors import *
logger = logging.getLogger(__name__)

class Controller:
    def __init__(self):
        self.model = CurrencyModel()

    def get_currencies(self):
        logger.info("Получение списка валют")
        try:
            currencies = self.model.get_currencies()
            logger.debug(f"Список валют: {currencies}")
            return currencies
        except Exception as e:
            logger.error(f"Ошибка при получении списка валют: {e}")
            raise APIError("Failed to retrieve currencies")

    def get_currency_by_code(self, code):
        logger.info("Получение валюты по коду")
        logger.debug(f"Код валюты из запроса: {code}")

        try:
            currency = self.model.get_currency_by_code(code)
            logger.info(f"Валюта найдена: {currency}")
            return currency

        except CurrencyNotFoundError as e:
            raise e
        except Exception as e:
            raise APIError()

    def add_currency(self, code):
        logger.info("Добавление новой валюты")
        if not code:
            raise MissingRequiredFieldsError()
        name, sign = currency_sign[code][0], currency_sign[code][1]
        currency_DTO = currencyDTO(code=code, name=name, sign=sign)
        try:
            return self.model.add_currency(currency_DTO.code, currency_DTO.name, currency_DTO.sign)
        except CurrencyAlreadyExistsError as e:
            raise e
        except Exception as e:
            raise APIError()

    def get_exchange_rates(self):
        logger.info("Получение всех курсов обмена валют")
        try:
            rates = self.model.get_exchange_rates()
            logger.debug(f"Курсы обмена: {rates}")
            return rates
        except Exception as e:
            raise APIError()

    def add_exchange_rate(self, from_currency, to_currency, rate):
        logger.info("Добавление нового курса обмена")

        if not from_currency or not to_currency or not rate:
            raise MissingRequiredFieldsError()

        try:
            base_currency = self.model.get_currency_by_code(from_currency)
            target_currency = self.model.get_currency_by_code(to_currency)
            logger.debug(f"Базовая валюта: {base_currency}, Целевая валюта: {target_currency}")
            if not base_currency or not target_currency:
                raise CurrencyNotFoundError(code=f"{from_currency or ''}{to_currency or ''}")

            self.model.add_exchange_rate(from_currency, to_currency, float(rate))
            result = self.model.get_exchange_rate(from_currency, to_currency)
            return {
                'id': result['id'],
                'baseCurrency': base_currency,
                'targetCurrency': target_currency,
                'rate': result['rate']
            }
        except CurrencyNotFoundError:  raise
        except CurrencyAlreadyExistsError:  raise 
        except ExchangeRateAlreadyExistsError:  raise 
        except Exception as e:
            raise APIError()

    def get_exchange_rate(self, from_currency, to_currency):
        logger.info("Просмотр курса обмена")
        if not from_currency or not to_currency:
            raise MissingRequiredFieldsError()
        try:
            result = self.model.get_exchange_rate(from_currency, to_currency)
            logger.debug(f"Курс обмена: {result}")
            if result:
                return {
                    'id': result['id'],
                    'baseCurrency': self.model.get_currency_by_code(from_currency),
                    'targetCurrency': self.model.get_currency_by_code(to_currency),
                    'rate': result['rate']
                }
            else:
                logger.error(f"Курс обмена не найден для валют: {from_currency} и {to_currency}")
                raise ExchangeRateNotFoundError(from_currency=from_currency, to_currency=to_currency)
        except ExchangeRateNotFoundError: raise    
        except Exception as e:
            raise APIError()

    def update_exchange_rate(self, from_currency, to_currency, rate):
        logger.info("Обновление курса обмена")
        if not from_currency or not to_currency:
            raise MissingRequiredFieldsError()
        try:
            self.model.patch_exchange_rate(from_currency, to_currency, float(rate))
            result = self.model.get_exchange_rate(from_currency, to_currency)
            return {
                'id': result['id'],
                'baseCurrency': self.model.get_currency_by_code(from_currency),
                'targetCurrency': self.model.get_currency_by_code(to_currency),
                'rate': result['rate']
            }
        except ExchangeRateNotFoundError as e:
            raise e
        except Exception as e:
            raise APIError()

    # def update_exchange_rate_by_pair(self, dto):
    #     logger.info("Обновление курса обмена по валютной паре")
    #     pair = dto.query_params.get('pair')
    #     rate = dto.body.get('rate')

    #     if not pair or not rate:
    #         raise MissingRequiredFieldsError()

    #     try:
    #         from_currency, to_currency = pair[:3], pair[3:]
    #         self.model.patch_exchange_rate(from_currency, to_currency, float(rate))
    #         self.get_exchange_rate(dto)
    #     except ExchangeRateNotFoundError as e:
    #         raise e
    #     except Exception as e:
    #         raise APIError()

    def convert_currency(self, from_currency, to_currency, amount):
        logger.info(f"Конвертация валюты: {amount} {from_currency} -> {to_currency}")

        if not from_currency or not to_currency or amount is None:
            raise MissingRequiredFieldsError()

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            raise InvalidAmountFormatError()

        try:
            result = self.model.get_conversion_info(from_currency, to_currency, amount, "USD")

            converted = round(amount * result["rate"], 2)

            return {
                "baseCurrency": result["baseCurrency"],
                "targetCurrency": result["targetCurrency"],
                "rate": result["rate"],
                "amount": round(amount, 2),
                "convertedAmount": converted
            }
        except ExchangeRateNotFoundError as e:
            logger.warning(f"Exchange rate not found: {e.message}")
            raise  # пробрасываем для обработки в роутере
        except CurrencyNotFoundError as e:
            logger.warning(f"Currency not found: {e.message}")
            raise  # пробрасываем для обработки в роутере
        except InvalidAmountFormatError as e:
            logger.warning(f"Invalid amount format: {e.message}")
            raise  # пробрасываем для обработки в роутере
        except Exception:
            logger.exception("Ошибка при конвертации валюты")
            raise APIError()



    def handle_html_page(self):
        logger.info("Обработка HTML-страницы")
        try:
            with open('index.html', 'r', encoding='utf-8') as file:

                return file.read()
        except FileNotFoundError:
            raise APIError()
