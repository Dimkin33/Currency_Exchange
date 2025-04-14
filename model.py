import sqlite3
import logging
from sign_code import currency_sign

logger = logging.getLogger(__name__)

class CurrencyModel:
    def __init__(self, db_path='currency.db'):
        self.db_path = db_path
        #logger.info(f"Инициализация CurrencyModel с базой данных: {db_path}")

    def init_db(self):
        logger.info("Инициализация базы данных")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS currencies (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                code TEXT NOT NULL UNIQUE,
                                name TEXT NOT NULL,
                                sign TEXT NOT NULL)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS exchange_rates (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                from_currency TEXT, 
                                to_currency TEXT,
                                rate REAL,
                                UNIQUE(from_currency, to_currency)
                                FOREIGN KEY (from_currency) REFERENCES currencies (code),
                                FOREIGN KEY (to_currency) REFERENCES currencies (code))''')
            conn.commit()
            logger.info("База данных успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
            raise
        finally:
            conn.close()

    def add_currency(self, code, name, sign):
        logger.info(f"Добавление валюты: {code}, {name}, {sign}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO currencies (code, name, sign) VALUES (?, ?, ?)', (code, name, sign))
            conn.commit()
            logger.debug(f"Валюта {code} успешно добавлена в базу данных")
        except sqlite3.IntegrityError:
            logger.warning(f"Валюта {code} уже существует в базе данных")
            raise ValueError("Currency already exists")
        except Exception as e:
            logger.error(f"Ошибка при добавлении валюты {code}: {e}")
            raise
        finally:
            conn.close()

    def get_currency_by_code(self, code):
        logger.info(f"Получение валюты по коду: {code}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, code, name, sign FROM currencies WHERE code = ?', (code,))
            result = cursor.fetchone()
            if result:
                logger.debug(f"Результат запроса: {result}")
                return {"id": result[0], "code": result[1], "name": result[2], "sign": result[3]}
            logger.warning(f"Валюта с кодом {code} не найдена")
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении валюты по коду {code}: {e}")
            raise
        finally:
            conn.close()

    def get_currencies(self):
        logger.info("Получение списка всех валют")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, code, name, sign FROM currencies')
            rows = cursor.fetchall()
            logger.debug(f"Список валют: {rows}")
            return [{"id": row[0], "code": row[1], "name": row[2], "sign": row[3]} for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении списка валют: {e}")
            raise
        finally:
            conn.close()

    def add_exchange_rate(self, from_currency, to_currency, rate):
        logger.info(f"Добавление курса обмена: {from_currency} -> {to_currency} = {rate}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO exchange_rates (from_currency, to_currency, rate) VALUES (?, ?, ?)', (from_currency, to_currency, rate))
            conn.commit()
            logger.debug(f"Курс обмена {from_currency} -> {to_currency} успешно добавлен")
            
        except sqlite3.IntegrityError:
            logger.warning(f"Курс обмена {from_currency} -> {to_currency} уже существует")
            raise ValueError("Exchange rate already exists")
        except Exception as e:
            logger.error(f"Ошибка при добавлении курса обмена {from_currency} -> {to_currency}: {e}")
            raise
        finally:
            conn.close()

    def patch_exchange_rate(self, from_currency, to_currency, rate):
        """
        Обновляет курс обмена между двумя валютами.
        """
        logger.info(f"Обновление курса обмена: {from_currency} -> {to_currency} = {rate}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Проверяем, существует ли запись для обновления
            cursor.execute('SELECT id FROM exchange_rates WHERE from_currency = ? AND to_currency = ?', (from_currency, to_currency))
            result = cursor.fetchone()
            if not result:
                logger.warning(f"Курс обмена {from_currency} -> {to_currency} не найден")
                raise ValueError("Exchange rate not found")

            # Обновляем курс обмена
            cursor.execute('UPDATE exchange_rates SET rate = ? WHERE from_currency = ? AND to_currency = ?', (rate, from_currency, to_currency))
            conn.commit()
            logger.info(f"Курс обмена {from_currency} -> {to_currency} успешно обновлен")
        except Exception as e:
            logger.error(f"Ошибка при обновлении курса обмена {from_currency} -> {to_currency}: {e}")
            raise
        finally:
            conn.close()

    def get_exchange_rates(self):
        logger.info("Получение курсов обмена валют")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, from_currency, to_currency, rate FROM exchange_rates')
            rows = cursor.fetchall()
            logger.debug(f"Результаты запроса курсов обмена: {rows}")
            return [
                {
                    "id": row[0],
                    "from": self.get_currency_by_code(row[1]),
                    "to":   self.get_currency_by_code(row[2]),
                    "rate": row[3]
                } for row in rows
            ]
        except Exception as e:
            logger.error(f"Ошибка при получении курсов обмена: {e}")
            raise
        finally:
            conn.close()

    def convert_currency(self, from_currency, to_currency, amount):
        logger.info(f"Конвертация валюты: {amount} {from_currency} -> {to_currency}")
        try:
            rates = self.get_exchange_rates()
            rate = next((r['rate'] for r in rates if r['from'] == from_currency and r['to'] == to_currency), None)
            if rate is None:
                logger.warning(f"Курс обмена {from_currency} -> {to_currency} не найден")
                raise ValueError("Exchange rate not found")
            converted_amount = amount * rate
            logger.info(f"Результат конвертации: {converted_amount} {to_currency}")
            return converted_amount
        except Exception as e:
            logger.error(f"Ошибка при конвертации валюты: {e}")
            raise

    def get_exchange_rate(self, from_currency, to_currency):
        logger.info(f"Получение курса обмена: {from_currency} -> {to_currency}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, rate FROM exchange_rates WHERE from_currency = ? AND to_currency = ?', (from_currency, to_currency))
            result = cursor.fetchone()
            if result:
                logger.debug(f"Курс обмена найден: {result[0]}")
                return {"from": from_currency, "to": to_currency, "rate": result[1], 'id': result[0]}
            logger.warning(f"Курс обмена {from_currency} -> {to_currency} не найден")
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении курса обмена {from_currency} -> {to_currency}: {e}")
            raise
        finally:
            conn.close()

