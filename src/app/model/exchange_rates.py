import sqlite3
import logging
from dto import CurrencyDTO, CurrencyExchangeDTO
from errors import ExchangeRateAlreadyExistsError, ExchangeRateNotFoundError, CurrencyNotFoundError

from .base import BaseModel

logger = logging.getLogger(__name__)


class ExchangeRateModel(BaseModel):
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> dict:
        conn, cursor = self._get_connection_and_cursor()
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

        base_currency = CurrencyDTO(base_id, base_code, base_name, base_sign).to_dict()
        target_currency = CurrencyDTO(
            target_id, target_code, target_name, target_sign
        ).to_dict()

        return CurrencyExchangeDTO(
            ex_id, base_currency, target_currency, rate
        ).to_dict()

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
            base_currency = CurrencyDTO(row[0], row[1], row[2], row[3]).to_dict()
            target_currency = CurrencyDTO(row[4], row[5], row[6], row[7]).to_dict()

            # 💾 Вставка курса
            cursor.execute(
                'INSERT INTO exchange_rates (from_currency, to_currency, rate) VALUES (?, ?, ?)',
                (from_currency, to_currency, rate),
            )
            conn.commit()
            exchange_id = cursor.lastrowid

            # 📤 Возврат в виде DTO
            return CurrencyExchangeDTO(
                exchange_id, base_currency, target_currency, rate
            ).to_dict()

        except sqlite3.IntegrityError as e:
            raise ExchangeRateAlreadyExistsError(from_currency, to_currency) from e

        except Exception:
            raise

    def patch_exchange_rate(
        self, from_currency: str, to_currency: str, rate: float
    ) -> dict:
        conn, cursor = self._get_connection_and_cursor()

        cursor.execute(
            'UPDATE exchange_rates SET rate = ? WHERE from_currency = ? AND to_currency = ?',
            (rate, from_currency.upper(), to_currency.upper()),
        )
        if cursor.rowcount == 0:
            raise ExchangeRateNotFoundError(from_currency, to_currency)
        conn.commit()
        return self.get_exchange_rate(from_currency, to_currency)

    def get_exchange_rates(self) -> list[dict]:
        conn, cursor = self._get_connection_and_cursor()

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

            base_currency = CurrencyDTO(
                base_id, base_code, base_name, base_sign
            ).to_dict()
            target_currency = CurrencyDTO(
                target_id, target_code, target_name, target_sign
            ).to_dict()

            exchange_dto = CurrencyExchangeDTO(
                ex_id, base_currency, target_currency, rate
            )
            result.append(exchange_dto.to_dict())

        return result
