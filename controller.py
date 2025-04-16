import logging
from model import CurrencyModel
from sign_code import currency_sign
from dto import currencyDTO, currencyExchangeDTO, requestDTO
from errors import APIError, CurrencyNotFoundError, InvalidCurrencyPairError, CurrencyAlreadyExistsError
logger = logging.getLogger(__name__)

# Логирование настроено в main.py, здесь используется существующая конфигурация

class Controller:
    def __init__(self):
        #logger.info("Инициализация Controller")
        self.model = CurrencyModel()

    def get_currencies(self, dto):
        logger.info("Получение списка валют")
        try:
            currencies = self.model.get_currencies()
            logger.debug(f"Список валют: {currencies}")
            dto.response = currencies
        except Exception as e:
            logger.error(f"Ошибка при получении списка валют: {e}")
            dto.response = {"error": "Failed to retrieve currencies"}

    def get_currency_by_code(self, dto):
        logger.info("Получение валюты по коду")
        code = dto.query_params.get('code', [None])
        logger.debug(f"Код валюты из запроса: {code}")
        if not code:
            raise InvalidCurrencyPairError("Currency code is required")
        try:
            currency = self.model.get_currency_by_code(code)
            logger.info(f"Валюта найдена: {currency}")
            dto.response = currency
            dto.status_code = 200  # Устанавливаем статус 200
            return currency
        except CurrencyNotFoundError as e:
            logger.warning(f"CurrencyNotFoundError: {e.message}")
            raise e
        except Exception as e:
            logger.error(f"Ошибка при получении валюты по коду {code}: {e}")
            raise APIError("Failed to retrieve currency")

    def get_currency_by_code_dynamic(self, dto):
        logger.info("Получение валюты по коду (динамический метод)")
        code = dto.query_params.get('code')
        logger.debug(f"Код валюты из запроса: {code}")
        if not code:
            logger.warning("Код валюты отсутствует в запросе")
            dto.response = {"error": "Currency code is required"}
            return
        currency = self.model.get_currency_by_code(code)
        if currency:
            logger.info(f"Валюта найдена: {currency}")
            dto.response = currency
            dto.status_code = 200  # Устанавливаем статус 200
        else:
            logger.warning(f"Валюта с кодом {code} не найдена")
            dto.response = {"error": "Currency not found"}
            dto.status_code = 404
            
    def get_exchange_rates_dynamic(self, dto):
        logger.info("Получение пары валют по коду (динамический метод)")
        logger.debug(f"Данные запроса: {dto.query_params}")
        pair = dto.query_params.get('pair')
        logger.debug(f"Коды валют из запроса: {pair}")
        if not pair:
            logger.warning("Код валюты отсутствует в запросе")
            dto.response = {"error": "Currency code is required"}
            return
        else:
            dto.body['from'] = pair[:3].upper()
            dto.body['to'] = pair[3:].upper()
            dto.query_params['from'] = pair[:3].upper()
            dto.query_params['to'] = pair[3:].upper()
        logger.debug(f"Коды валют из запроса: {dto.body['from']}, {dto.body['to']}")
        self.get_exchange_rate(dto)
        
        

    def add_currency(self, dto):
        logger.info("Добавление новой валюты")
        logger.debug(f"Данные запроса: {dto.body}")
        code = dto.body.get('code')
        # name = dto.body.get('name')
        # sign = dto.body.get('sign')
        name = currency_sign[code][0]
        sign = currency_sign[code][1]
        
        currency_DTO = currencyDTO(code=code, name=name, sign=sign)
        
        if not code:
            logger.warning("Отсутствуют обязательные поля для добавления валюты")
            raise Missing_required_fields("Missing required fields")
            return
        try:
            self.model.add_currency(currency_DTO.code, currency_DTO.name, currency_DTO.sign)
            logger.info(f"Валюта {code} успешно добавлена")
            dto.response = curency_DTO.to_dict()
            dto.status_code = 201  # Created
        except CurrencyAlreadyExistsError as e:
            raise e  # пробрасываем дальше в router для централизованной обработки
        except Exception as e:
            dto.response = {"error": "Failed to add currency"}
            dto.status_code = 500

    def get_exchange_rates(self, dto):
        logger.info("Получение курсов обмена валют")
        try:
            rates = self.model.get_exchange_rates()
            logger.debug(f"Курсы обмена: {rates}")
            dto.response = rates
        except Exception as e:
            logger.error(f"Ошибка при получении курсов обмена: {e}")
            dto.response = {"error": "Failed to retrieve exchange rates"}

    def add_exchange_rate(self, dto):
        logger.info("Добавление нового курса обмена")
        logger.debug(f"Данные запроса: {dto.body}")
        from_currency = dto.body.get('from')
        to_currency = dto.body.get('to')
        rate = dto.body.get('rate')

        # Проверка обязательных полей
        if not from_currency or not to_currency or not rate:
            logger.warning("Отсутствуют обязательные поля для добавления курса обмена")
            dto.response = {"error": "Missing required fields"}
            dto.status_code = 400  # Bad Request
            return

        try:
            # Проверяем, существуют ли валюты в базе данных
            base_currency = self.model.get_currency_by_code(from_currency)
            target_currency = self.model.get_currency_by_code(to_currency)
            if not base_currency or not target_currency:
                logger.warning(f"Одна или обе валюты не найдены: {from_currency}, {to_currency}")
                dto.response = {"error": "One or both currencies not found"}
                dto.status_code = 404  # Not Found
                return

            # Добавляем курс обмена
            self.model.add_exchange_rate(from_currency, to_currency, float(rate))
            logger.info(f"Курс обмена {from_currency} -> {to_currency} успешно добавлен")

            # Получаем добавленный курс для ответа
            result = self.model.get_exchange_rate(from_currency, to_currency)
            dto.response = {
                'id': result['id'],
                'baseCurrency': base_currency,
                'targetCurrency': target_currency,
                'rate': result['rate']
            }
            dto.status_code = 201  # Created

        except ValueError as e:
            # Если курс обмена уже существует
            logger.error(f"Ошибка при добавлении курса обмена: {e}")
            dto.response = {"error": str(e)}
            dto.status_code = 409  # Conflict

        except Exception as e:
            # Общая ошибка
            logger.critical(f"Неизвестная ошибка при добавлении курса обмена: {e}")
            dto.response = {"error": "Failed to add exchange rate"}
            dto.status_code = 500  # Internal Server Error

    def get_exchange_rate(self, dto):
        logger.info("Просмотр курса обмена")
        logger.debug(f"Данные запроса: {dto.query_params}")
        from_currency = dto.query_params.get('from')
        to_currency = dto.query_params.get('to')
        #rate = dto.body.get('rate
        if not from_currency or not to_currency:
            logger.warning("Отсутствуют обязательные поля для просмотра курса обмена")
            dto.response = {"error": "Missing required fields"}
            return
        try:
            result = self.model.get_exchange_rate(from_currency, to_currency)
            if result:
                logger.info(f"Курс обмена {from_currency} -> {to_currency} успешно получен result = {result}")
                dto.response = {'id' : result['id'],
                                'baseCurrency' : self.model.get_currency_by_code(from_currency), 
                                'targetCurrency' : self.model.get_currency_by_code(to_currency),
                                'rate' : result['rate']
                                }
            else:
                logger.debug(f"Курс обмена {from_currency} -> {to_currency}: {result}")
                dto.response = {"error": "Exchange rate not found"}
        except ValueError as e:
            logger.error(f"Ошибка при добавлении курса обмена: {e}")
            dto.response = {"error": str(e)}
            
    def update_exchange_rate(self, dto):
        logger.info("Добавление нового курса обмена")
        logger.debug(f"Данные запроса: {dto.body}")
        from_currency = dto.body.get('from')
        to_currency = dto.body.get('to')
        rate = dto.body.get('rate')
        if not from_currency or not to_currency:
            logger.warning("Отсутствуют обязательные поля для добавления курса обмена")
            dto.response = {"error": "Missing required fields"}
            return
        try:
            result = self.model.patch_exchange_rate(from_currency, to_currency, float(rate))
            logger.info(f"Курс обмена {from_currency} -> {to_currency} успешно добавлен")
            result = self.model.get_exchange_rate(from_currency, to_currency)
            logger.debug(f"Курс обмена {from_currency} -> {to_currency}: {result}")
            logger.info(f"Курс обмена {from_currency} -> {to_currency} успешно получен result = {result}")
            dto.response = {'id' : result['id'],
                            'baseCurrency' : self.model.get_currency_by_code(from_currency), 
                            'targetCurrency' : self.model.get_currency_by_code(to_currency),
                            'rate' : result['rate']
                            }
                            
        except ValueError as e:
            logger.error(f"Ошибка при добавлении курса обмена: {e}")
            dto.response = {"error": str(e)}

    def update_exchange_rate_by_pair(self, dto):
        logger.info("Обновление курса обмена по валютной паре")
        logger.debug(f"Данные запроса: {dto.body}, параметры: {dto.query_params}")

        pair = dto.query_params.get('pair')
        rate = dto.body.get('rate')

        if not pair or not rate:
            logger.warning("Отсутствуют обязательные поля для обновления курса обмена")
            dto.response = {"error": "Missing required fields"}
            dto.status_code = 400  # Bad Request
            return

        try:
            from_currency, to_currency = pair[:3], pair[3:]  # Разделяем пару на две валюты
            self.model.patch_exchange_rate(from_currency, to_currency, float(rate))
            self.model.get_exchange_rate(from_currency, to_currency)
            #dto.response = {"message": f"Exchange rate {from_currency} -> {to_currency} updated successfully"}
            #dto.status_code = 200  # OK
        except ValueError as e:
            logger.error(f"Ошибка при обновлении курса обмена: {e}")
            dto.response = {"error": str(e)}
            dto.status_code = 404  # Not Found
        except Exception as e:
            logger.critical(f"Неизвестная ошибка при обновлении курса обмена: {e}")
            dto.response = {"error": "Failed to update exchange rate"}
            dto.status_code = 500  # Internal Server Error

    def convert_currency(self, dto):
        logger.info("Конвертация валюты")
        from_currency = dto.query_params.get('from', [None])[0]
        to_currency = dto.query_params.get('to', [None])[0]
        amount = dto.query_params.get('amount', [None])[0]
        logger.debug(f"Параметры конвертации: from={from_currency}, to={to_currency}, amount={amount}")
        if not from_currency or not to_currency or not amount:
            logger.warning("Отсутствуют обязательные параметры для конвертации валюты")
            dto.response = {"error": "Missing required parameters"}
            return
        try:
            amount = float(amount)
            converted_amount = self.model.convert_currency(from_currency, to_currency, amount)
            logger.info(f"Конвертация завершена: {amount} {from_currency} -> {converted_amount} {to_currency}")
            dto.response = {"converted_amount": converted_amount}
        except ValueError as e:
            logger.error(f"Ошибка при конвертации валюты: {e}")
            dto.response = {"error": str(e)}

    def handle_html_page(self, dto):
        logger.info("Обработка HTML-страницы")
        try:
            with open('index.html', 'r', encoding='utf-8') as file:
                html_content = file.read()
            logger.debug("HTML-страница успешно загружена")
            dto.response = html_content
        except FileNotFoundError:
            logger.error("HTML-файл не найден")
            dto.response = {"error": "HTML file not found"}

