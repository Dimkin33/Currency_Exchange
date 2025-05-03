import sqlite3

from dto import currencyDTO, currencyExchangeDTO
from errors import ExchangeRateAlreadyExistsError, ExchangeRateNotFoundError

from .base import BaseModel


class ExchangeRateModel(BaseModel):
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> dict:
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
            WHERE er.from_currency = ? AND er.to_currency = ?
        """, (from_currency.upper(), to_currency.upper()))
        row = cursor.fetchone()

        if not row:
            raise ExchangeRateNotFoundError(from_currency, to_currency)

        (
            ex_id,
            base_id, base_code, base_name, base_sign,
            target_id, target_code, target_name, target_sign,
            rate
        ) = row

        base_currency = currencyDTO(base_id, base_code, base_name, base_sign).to_dict()
        target_currency = currencyDTO(target_id, target_code, target_name, target_sign).to_dict()

        return currencyExchangeDTO(ex_id, base_currency, target_currency, rate).to_dict()


    def add_exchange_rate(self, from_currency: str, to_currency: str, rate: float):
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        conn, cursor = self._get_connection_and_cursor()
        try:
            cursor.execute(
                "INSERT INTO exchange_rates (from_currency, to_currency, rate) VALUES (?, ?, ?)",
                (from_currency, to_currency, rate)
            )
            conn.commit()
            exchange_id = cursor.lastrowid
            return {"id": exchange_id, "from_currency": from_currency, "to_currency": to_currency, "rate": rate}
        except sqlite3.IntegrityError:
            raise ExchangeRateAlreadyExistsError(from_currency, to_currency)


    def patch_exchange_rate(self, from_currency: str, to_currency: str, rate: float) -> dict:
        conn, cursor = self._get_connection_and_cursor()

        cursor.execute("UPDATE exchange_rates SET rate = ? WHERE from_currency = ? AND to_currency = ?",
                        (rate, from_currency.upper(), to_currency.upper()))
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
                base_id, base_code, base_name, base_sign,
                target_id, target_code, target_name, target_sign,
                rate
            ) = row

            base_currency = currencyDTO(base_id, base_code, base_name, base_sign).to_dict()
            target_currency = currencyDTO(target_id, target_code, target_name, target_sign).to_dict()

            exchange_dto = currencyExchangeDTO(ex_id, base_currency, target_currency, rate)
            result.append(exchange_dto.to_dict())

        return result
