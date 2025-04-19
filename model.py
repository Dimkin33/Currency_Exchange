import sqlite3
import logging
from sign_code import currency_sign
from dto import currencyDTO, currencyExchangeDTO
from errors import CurrencyNotFoundError, CurrencyAlreadyExistsError, ExchangeRateNotFoundError, ExchangeRateAlreadyExistsError 

logger = logging.getLogger(__name__)

class CurrencyModel:
    def __init__(self, db_path='currency.db'):
        self.db_path = db_path
        #logger.info(f"Инициализация CurrencyModel с базой данных: {db_path}")

    def _get_connection_and_cursor(self):
        """
        Вспомогательный метод для получения соединения и курсора SQLite.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        return conn, cursor

    def init_db(self):
        logger.info("Инициализация базы данных")
        conn, cursor = self._get_connection_and_cursor()
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
                                UNIQUE(from_currency, to_currency),
                                FOREIGN KEY (from_currency) REFERENCES currencies (code),
                                FOREIGN KEY (to_currency) REFERENCES currencies (code))''')
            conn.commit()
            logger.info("База данных успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
            raise
        finally:
            conn.close()

    def add_currency(self, code: str, name: str, sign: str) -> dict:
        try:
            conn, cursor = self._get_connection_and_cursor()
            cursor.execute(
                'INSERT INTO currencies (code, name, sign) VALUES (?, ?, ?)',
                (code.upper(), name, sign)
            )
            currency_id = cursor.lastrowid  # ← Получаем ID новой валюты
            conn.commit()

            return {
                "id": currency_id,
                "code": code.upper(),
                "name": name,
                "sign": sign
            }

        except sqlite3.IntegrityError:
            raise CurrencyAlreadyExistsError(code=code.upper())
        finally:
            conn.close()

    def get_currency_by_code(self, code : str) -> dict:
        logger.info(f"Получение валюты по коду: {code}")
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute('SELECT id, code, name, sign FROM currencies WHERE code = ?', (code.upper(),))
            result = cursor.fetchone()
            if result:
                logger.debug(f"Результат запроса: {result}")
                return {"id": result[0], "code": result[1], "name": result[2], "sign": result[3]}
            logger.warning(f"Валюта с кодом {code} не найдена")
            raise CurrencyNotFoundError(code)
        except Exception as e:
            logger.error(f"Ошибка при получении валюты по коду {code}: {e}")
            raise
        finally:
            conn.close()

    def get_currencies(self):
        logger.info("Получение списка всех валют")
        conn, cursor = self._get_connection_and_cursor()
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

    def add_exchange_rate(self, from_currency: str, to_currency: str, rate: float):
        logger.info(f"Добавление курса обмена: {from_currency} -> {to_currency} = {rate}")
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute(
                'INSERT INTO exchange_rates (from_currency, to_currency, rate) VALUES (?, ?, ?)',
                (from_currency, to_currency, rate)
            )
            conn.commit()
            logger.debug(f"Курс обмена {from_currency} -> {to_currency} успешно добавлен")

        except sqlite3.IntegrityError:
            logger.warning(f"Курс обмена {from_currency} -> {to_currency} уже существует")
            raise ExchangeRateAlreadyExistsError(from_currency=from_currency, to_currency=to_currency)

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
        conn, cursor = self._get_connection_and_cursor()
        try:
            # Проверяем, существует ли запись для обновления
            cursor.execute('SELECT id FROM exchange_rates WHERE from_currency = ? AND to_currency = ?', (from_currency, to_currency))
            result = cursor.fetchone()
            logger.debug(f"result: {result}")
            if not result:
                logger.warning(f"Курс обмена {from_currency} -> {to_currency} не найден")
                raise ValueError("Exchange rate not found")

            # Обновляем курс обмена
            cursor.execute('UPDATE exchange_rates SET rate = ? WHERE from_currency = ? AND to_currency = ?', (rate, from_currency, to_currency))
            conn.commit()
            logger.info(f"Курс обмена {from_currency} -> {to_currency} успешно обновлен")
            return self.get_exchange_rate(from_currency, to_currency)
        except Exception as e:
            logger.error(f"Ошибка при обновлении курса обмена {from_currency} -> {to_currency}: {e}")
            raise
        finally:
            conn.close()

    def get_exchange_rates(self):
        logger.info("Получение курсов обмена валют (через JOIN)")
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute("""
                SELECT 
                    er.id,
                    f.code, f.name, f.sign,
                    t.code, t.name, t.sign,
                    er.rate
                FROM exchange_rates er
                JOIN currencies f ON er.from_currency = f.code
                JOIN currencies t ON er.to_currency = t.code
            """)
            rows = cursor.fetchall()
            logger.debug(f"Результаты запроса: {rows}")

            exchange_rates = []
            for row in rows:
                exchange_rates.append({
                    "id": row[0],
                    "from": {
                        "code": row[1],
                        "name": row[2],
                        "sign": row[3],
                    },
                    "to": {
                        "code": row[4],
                        "name": row[5],
                        "sign": row[6],
                    },
                    "rate": row[7]
                })

            return exchange_rates

        except Exception as e:
            logger.error(f"Ошибка при получении курсов обмена: {e}")
            raise
        finally:
            conn.close()

    def get_exchange_rate(self, from_currency, to_currency):
        logger.info(f"Получение курса обмена: {from_currency} -> {to_currency}")
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute('SELECT id, rate FROM exchange_rates WHERE from_currency = ? AND to_currency = ?', (from_currency, to_currency))
            result = cursor.fetchone()
            if result:
                logger.debug(f"Курс обмена найден: {result}")
                return {"from": from_currency, "to": to_currency, "rate": result[1], 'id': result[0]}
            logger.warning(f"Курс обмена {from_currency} -> {to_currency} не найден")
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении курса обмена {from_currency} -> {to_currency}: {e}")
            raise
        finally:
            conn.close()

    def get_conversion_info(self, from_currency: str, to_currency: str, amount: float, base_currency='USD') -> dict:
        logger.info(f"Получение данных для конвертации (одним SQL-запросом): {from_currency} -> {to_currency}")
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute("""
                SELECT
                    COALESCE(
                        (SELECT rate FROM exchange_rates WHERE from_currency = ? AND to_currency = ?),
                        (SELECT 1.0 / rate FROM exchange_rates WHERE from_currency = ? AND to_currency = ?),
                        (
                            (SELECT rate FROM exchange_rates WHERE from_currency = ? AND to_currency = ?) / 
                            (SELECT rate FROM exchange_rates WHERE from_currency = ? AND to_currency = ?)
                        )
                    ) AS rate,

                    bc.id, bc.code, bc.name, bc.sign,
                    tc.id, tc.code, tc.name, tc.sign

                FROM currencies bc, currencies tc
                WHERE bc.code = ? AND tc.code = ?
            """, (
                from_currency.upper(), to_currency.upper(),
                to_currency.upper(), from_currency.upper(),
                base_currency.upper(), to_currency.upper(),
                base_currency.upper(), from_currency.upper(),
                from_currency.upper(), to_currency.upper()
            ))

            row = cursor.fetchone()

            if not row or row[0] is None:
                raise ExchangeRateNotFoundError(from_currency=from_currency, to_currency=to_currency)

            rate = row[0]
            converted = round(amount * rate, 2)

            return {
                "baseCurrency": {
                    "id": row[1],
                    "code": row[2],
                    "name": row[3],
                    "sign": row[4]
                },
                "targetCurrency": {
                    "id": row[5],
                    "code": row[6],
                    "name": row[7],
                    "sign": row[8]
                },
                "rate": rate,
                "amount": round(amount, 2),
                "convertedAmount": converted
            }

        except Exception as e:
            logger.exception("Ошибка при получении данных для конвертации")
            raise
        finally:
            conn.close()

