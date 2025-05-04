import logging
import sqlite3

from dto import currencyDTO, currencyExchangeDTO
from errors import (
    CurrencyAlreadyExistsError,
    CurrencyNotFoundError,
    ExchangeRateAlreadyExistsError,
    ExchangeRateNotFoundError,
)

logger = logging.getLogger(__name__)


class CurrencyModel:
    def __init__(self, connector: sqlite3 = None):
        self.connector = connector
        logger.info(f'Инициализация CurrencyModel с коннектором {self.connector}')

    def _get_connection_and_cursor(self):
        return self.connector, self.connector.cursor()

    def get_currency_by_code(self, code: str) -> dict:
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute(
                'SELECT id, code, name, sign FROM currencies WHERE code = ?', (code,)
            )
            row = cursor.fetchone()
            if not row:
                raise CurrencyNotFoundError(code)
            return currencyDTO(*row).to_dict()
        except Exception:
            raise

    def delete_all_currencies(self):
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.executescript("""
                DELETE FROM exchange_rates;
                DELETE FROM currencies;
                DELETE FROM sqlite_sequence WHERE name='exchange_rates';
                DELETE FROM sqlite_sequence WHERE name='currencies';
            """)
            conn.commit()
            return {'message': 'All currencies and exchange rates deleted, ids reset'}
        except Exception:
            raise

    def get_currencies(self) -> list[dict]:
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute('SELECT id, code, name, sign FROM currencies')
            rows = cursor.fetchall()
            return [currencyDTO(*row).to_dict() for row in rows]
        except Exception:
            raise

    def add_currency(self, code: str, name: str, sign: str) -> dict:
        code = code.upper()
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute(
                'INSERT INTO currencies (code, name, sign) VALUES (?, ?, ?)',
                (code, name, sign),
            )
            conn.commit()
            currency_id = cursor.lastrowid
            return currencyDTO(currency_id, code, name, sign).to_dict()
        except sqlite3.IntegrityError:
            raise CurrencyAlreadyExistsError(code)
        except Exception:
            raise

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> dict:
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute(
                """
                SELECT
                    er.id,
                    base.id, base.code, base.name, base.sign,
                    target.id, target.code, target.name, target.sign,
                    er.rate
                FROM exchange_rates er
                JOIN currencies base ON er.from_currency = base.code
                JOIN currencies target ON er.to_currency = target.code
                WHERE er.from_currency = ? AND er.to_currency = ?
            """,
                (from_currency.upper(), to_currency.upper()),
            )
            row = cursor.fetchone()

            if not row:
                raise ExchangeRateNotFoundError(from_currency, to_currency)

            (
                ex_id,
                base_id,
                base_code,
                base_name,
                base_sign,
                target_id,
                target_code,
                target_name,
                target_sign,
                rate,
            ) = row

            base_currency = currencyDTO(
                base_id, base_code, base_name, base_sign
            ).to_dict()
            target_currency = currencyDTO(
                target_id, target_code, target_name, target_sign
            ).to_dict()

            return currencyExchangeDTO(
                ex_id, base_currency, target_currency, rate
            ).to_dict()

        except Exception:
            raise

    def get_exchange_rates(self) -> list[dict]:
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute("""
                    SELECT
                        er.id,
                        base.id, base.code, base.name, base.sign,
                        target.id, target.code, target.name, target.sign,
                        er.rate
                    FROM exchange_rates er
                    JOIN currencies base ON er.from_currency = base.code
                    JOIN currencies target ON er.to_currency = target.code
                """)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                (
                    ex_id,
                    base_id,
                    base_code,
                    base_name,
                    base_sign,
                    target_id,
                    target_code,
                    target_name,
                    target_sign,
                    rate,
                ) = row

                base_currency = currencyDTO(
                    base_id, base_code, base_name, base_sign
                ).to_dict()
                target_currency = currencyDTO(
                    target_id, target_code, target_name, target_sign
                ).to_dict()

                exchange_dto = currencyExchangeDTO(
                    ex_id, base_currency, target_currency, rate
                )
                result.append(exchange_dto.to_dict())

            return result
        except Exception:
            raise

    def get_conversion_info(
        self, from_currency: str, to_currency: str, amount: float
    ) -> dict:
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute(
                """
                    SELECT
                        er.rate,
                        base.id, base.code, base.name, base.sign,
                        target.id, target.code, target.name, target.sign
                    FROM exchange_rates er
                    JOIN currencies base ON er.from_currency = base.code
                    JOIN currencies target ON er.to_currency = target.code
                    WHERE er.from_currency = ? AND er.to_currency = ?
                """,
                (from_currency.upper(), to_currency.upper()),
            )
            row = cursor.fetchone()

            if not row:
                raise ExchangeRateNotFoundError(from_currency, to_currency)

            (
                rate,
                base_id,
                base_code,
                base_name,
                base_sign,
                target_id,
                target_code,
                target_name,
                target_sign,
            ) = row

            converted_amount = round(rate * amount, 2)

            return {
                'baseCurrency': currencyDTO(
                    base_id, base_code, base_name, base_sign
                ).to_dict(),
                'targetCurrency': currencyDTO(
                    target_id, target_code, target_name, target_sign
                ).to_dict(),
                'rate': rate,
                'amount': amount,
                'convertedAmount': converted_amount,
            }
        except Exception:
            raise

    def add_exchange_rate(self, from_currency: str, to_currency: str, rate: float):
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        conn, cursor = self._get_connection_and_cursor()

        logger.info(f'Adding exchange rate: {from_currency} -> {to_currency} = {rate}')

        try:
            # 🔍 Проверка существования валют
            cursor.execute(
                'SELECT code FROM currencies WHERE code IN (?, ?)',
                (from_currency, to_currency),
            )
            found_codes = {row[0] for row in cursor.fetchall()}
            missing_codes = {from_currency, to_currency} - found_codes
            if missing_codes:
                raise CurrencyNotFoundError(*missing_codes)

            # 📦 Получение информации о валютах через JOIN
            cursor.execute(
                """
                SELECT 
                    base.id, base.code, base.name, base.sign,
                    target.id, target.code, target.name, target.sign
                FROM currencies base
                JOIN currencies target ON target.code = ?
                WHERE base.code = ?
            """,
                (to_currency, from_currency),
            )

            row = cursor.fetchone()
            base_currency = currencyDTO(row[0], row[1], row[2], row[3]).to_dict()
            target_currency = currencyDTO(row[4], row[5], row[6], row[7]).to_dict()

            # 💾 Вставка курса
            cursor.execute(
                'INSERT INTO exchange_rates (from_currency, to_currency, rate) VALUES (?, ?, ?)',
                (from_currency, to_currency, rate),
            )
            conn.commit()
            exchange_id = cursor.lastrowid

            # 📤 Возврат в виде DTO
            return currencyExchangeDTO(
                exchange_id, base_currency, target_currency, rate
            ).to_dict()

        except sqlite3.IntegrityError:
            raise ExchangeRateAlreadyExistsError(from_currency, to_currency)

        except Exception:
            raise

    def patch_exchange_rate(
        self, from_currency: str, to_currency: str, rate: float
    ) -> dict:
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute(
                'UPDATE exchange_rates SET rate = ? WHERE from_currency = ? AND to_currency = ?',
                (rate, from_currency.upper(), to_currency.upper()),
            )
            if cursor.rowcount == 0:
                raise ExchangeRateNotFoundError(from_currency, to_currency)
            conn.commit()
            return self.get_exchange_rate(from_currency, to_currency)
        finally:
            conn.close()

    def get_converted_currency(
        self, from_currency: str, to_currency: str, amount: float
    ) -> dict:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        conn, cursor = self._get_connection_and_cursor()

        try:
            query = """
            SELECT 'direct' AS source,
                er.id,
                base.id, base.code, base.name, base.sign,
                target.id, target.code, target.name, target.sign,
                er.rate
            FROM exchange_rates er
            JOIN currencies base ON er.from_currency = base.code
            JOIN currencies target ON er.to_currency = target.code
            WHERE er.from_currency = ? AND er.to_currency = ?

            UNION ALL

            SELECT 'reverse' AS source,
                er.id,
                target.id, target.code, target.name, target.sign,
                base.id, base.code, base.name, base.sign,
                1.0 / er.rate
            FROM exchange_rates er
            JOIN currencies base ON er.from_currency = base.code
            JOIN currencies target ON er.to_currency = target.code
            WHERE er.from_currency = ? AND er.to_currency = ?

            UNION ALL

            SELECT 'via_usd' AS source,
                -1,
                cur1.id, cur1.code, cur1.name, cur1.sign,
                cur2.id, cur2.code, cur2.name, cur2.sign,
                r2.rate / r1.rate
            FROM exchange_rates r1
            JOIN exchange_rates r2 ON r1.from_currency = ? AND r2.from_currency = ?
            JOIN currencies cur1 ON cur1.code = ?
            JOIN currencies cur2 ON cur2.code = ?
            WHERE r1.to_currency = ? AND r2.to_currency = ?

            """
            base = 'USD'
            cursor.execute(
                query,
                (
                    from_currency,
                    to_currency,
                    to_currency,
                    from_currency,
                    base,
                    base,
                    from_currency,
                    to_currency,
                    from_currency,
                    to_currency,
                ),
            )

            row = cursor.fetchone()
            if not row:
                raise ExchangeRateNotFoundError(from_currency, to_currency)

            source = row[0]  # 'direct', 'reverse' или 'via_usd'

            logger.info(f'Метод определения источника курса: {source}')

            (
                ex_id,
                base_id,
                base_code,
                base_name,
                base_sign,
                target_id,
                target_code,
                target_name,
                target_sign,
                rate,
            ) = row[1:]  # Получение значений из кортежа row, начиная с индекса 1

            base_currency = currencyDTO(
                base_id, base_code, base_name, base_sign
            ).to_dict()
            target_currency = currencyDTO(
                target_id, target_code, target_name, target_sign
            ).to_dict()

            return currencyExchangeDTO(
                ex_id,
                base_currency,
                target_currency,
                round(rate, 2),
                round(amount, 2),
                round(rate * amount, 2),
                source,
            ).to_converted_dict()

        finally:
            conn.close()
