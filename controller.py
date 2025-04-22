import logging
from model import CurrencyModel
from sign_code import currency_sign
from dto import currencyDTO, currencyExchangeDTO, requestDTO
from errors import *
from typing import Any

logger = logging.getLogger(__name__)

class Controller:
    """
    Контроллер для обработки бизнес-логики приложения.
    """

    def __init__(self) -> None:
        """
        Инициализация контроллера с моделью данных.
        """
        self.model = CurrencyModel()

    def get_currencies(self, dto: requestDTO) -> None:
        """
        Получение списка всех валют.

        :param dto: Объект DTO для передачи данных между слоями.
        """
        logger.info("Получение списка валют")
        try:
            currencies = self.model.get_currencies()
            logger.debug(f"Список валют: {currencies}")
            dto.response = currencies
        except Exception as e:
            logger.error(f"Ошибка при получении списка валют: {e}")
            dto.response = {"error": "Failed to retrieve currencies"}

    def get_currency_by_code(self, dto: requestDTO) -> None:
        """
        Получение валюты по коду.

        :param dto: Объект DTO с параметрами запроса.
        """
        logger.info("Получение валюты по коду")

        if not isinstance(dto, requestDTO):
            logger.error("Неверный тип объекта dto. Ожидался requestDTO.")
            raise TypeError("Invalid type for dto. Expected requestDTO.")

        code = dto.query_params.get('code', [None])
        logger.debug(f"Код валюты из запроса: {code}")
        if not code:
            raise InvalidCurrencyPairError("Currency code is required")
        try:
            currency = self.model.get_currency_by_code(code)
            logger.info(f"Валюта найдена: {currency}")
            dto.response = currency
        except CurrencyNotFoundError as e:
            logger.warning(f"CurrencyNotFoundError: {e.message}")
            raise e
        except Exception as e:
            logger.error(f"Ошибка при получении валюты по коду {code}: {e}")
            raise APIError("Failed to retrieve currency")

    def add_currency(self, dto: requestDTO) -> None:
        """
        Добавление новой валюты.

        :param dto: Объект DTO с данными для добавления валюты.
        """
        logger.info("Добавление новой валюты")
        logger.debug(f"Данные запроса: {dto.body}")
        code = dto.body.get('code')
        name = currency_sign[code][0]
        sign = currency_sign[code][1]

        if not code:
            logger.warning("Отсутствуют обязательные поля для добавления валюты")
            dto.response = {"error": "Missing required fields"}
            return
        try:
            self.model.add_currency(code, name, sign)
            logger.info(f"Валюта {code} успешно добавлена")
            dto.response = self.model.get_currency_by_code(code)
        except ValueError as e:
            logger.error(f"Ошибка при добавлении валюты {code}: {e}")
            dto.response = {"error": str(e)}
        except Exception as e:
            logger.critical(f"Неизвестная ошибка при добавлении валюты {code}: {e}")
            dto.response = {"error": "Failed to add currency"}

    def get_exchange_rates(self) -> Any:
        """
        Получение всех курсов обмена валют.

        :return: Список курсов обмена валют.
        """
        logger.info("Получение всех курсов обмена валют")
        try:
            rates = self.model.get_exchange_rates()
            logger.debug(f"Курсы обмена: {rates}")
            return rates
        except Exception as e:
            raise APIError()

    def add_exchange_rate(self, from_currency: str, to_currency: str, rate: float) -> dict:
        """
        Добавление нового курса обмена.

        :param from_currency: Код базовой валюты.
        :param to_currency: Код целевой валюты.
        :param rate: Курс обмена.
        :return: Словарь с информацией о добавленном курсе обмена.
        """
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

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> dict:
        """
        Просмотр курса обмена.

        :param from_currency: Код базовой валюты.
        :param to_currency: Код целевой валюты.
        :return: Словарь с информацией о курсе обмена.
        """
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

    def update_exchange_rate(self, from_currency: str, to_currency: str, rate: float) -> dict:
        """
        Обновление курса обмена.

        :param from_currency: Код базовой валюты.
        :param to_currency: Код целевой валюты.
        :param rate: Новый курс обмена.
        :return: Словарь с информацией об обновленном курсе обмена.
        """
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

    def convert_currency(self, from_currency: str, to_currency: str, amount: float) -> dict:
        """
        Конвертация валюты.

        :param from_currency: Код базовой валюты.
        :param to_currency: Код целевой валюты.
        :param amount: Сумма для конвертации.
        :return: Словарь с информацией о конвертации валюты.
        """
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

    def handle_html_page(self) -> str:
        """
        Обработка HTML-страницы.

        :return: Содержимое HTML-страницы.
        """
        logger.info("Обработка HTML-страницы")
        try:
            with open('index.html', 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise APIError()
