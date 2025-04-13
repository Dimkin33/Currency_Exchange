import logging
from model import CurrencyModel
from sign_code import currency_sign

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
        code = dto.query_params.get('code', [None])[0]
        logger.debug(f"Код валюты из запроса: {code}")
        if not code:
            logger.warning("Код валюты отсутствует в запросе")
            dto.response = {"error": "Currency code is required"}
            return
        try:
            currency = self.model.get_currency_by_code(code)
            if currency:
                logger.info(f"Валюта найдена: {currency}")
                dto.response = currency
            else:
                logger.warning(f"Валюта с кодом {code} не найдена")
                dto.response = {"error": "Currency not found"}
        except Exception as e:
            logger.error(f"Ошибка при получении валюты по коду {code}: {e}")
            dto.response = {"error": "Failed to retrieve currency"}

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
        else:
            logger.warning(f"Валюта с кодом {code} не найдена")
            dto.response = {"error": "Currency not found"}
            
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
        if not from_currency or not to_currency:
            logger.warning("Отсутствуют обязательные поля для добавления курса обмена")
            dto.response = {"error": "Missing required fields"}
            return
        try:
            result = self.model.add_exchange_rate(from_currency, to_currency, float(rate))
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
                logger.debug(f"Курс обмена {from_currency} -> {to_currency}: {result}")
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

