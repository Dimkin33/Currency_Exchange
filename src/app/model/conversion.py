import logging

from dto import currencyDTO, currencyExchangeDTO
from errors import ExchangeRateNotFoundError

from .base import BaseModel

logger = logging.getLogger(__name__)


class ConversionModel(BaseModel):
    def get_converted_currency(self, from_currency: str, to_currency: str, amount: float) -> dict:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        conn, cursor = self._get_connection_and_cursor()


        query = '''
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

        '''
        base = 'USD'
        cursor.execute(query, (
            from_currency, to_currency,
            to_currency, from_currency,
            base, base,
            from_currency, to_currency,
            from_currency, to_currency
        ))

        row = cursor.fetchone()
        if not row:
            raise ExchangeRateNotFoundError(from_currency, to_currency)

        source = row[0]  # 'direct', 'reverse' или 'via_usd'

        logger.info(f"Метод определения источника курса: {source}")

        (
            ex_id,
            base_id, base_code, base_name, base_sign,
            target_id, target_code, target_name, target_sign,
            rate
        ) = row[1:] # Получение значений из кортежа row, начиная с индекса 1

        base_currency = currencyDTO(base_id, base_code, base_name, base_sign).to_dict()
        target_currency = currencyDTO(target_id, target_code, target_name, target_sign).to_dict()

        return currencyExchangeDTO(ex_id, base_currency, target_currency, round(rate, 2), round(amount, 2), round(rate * amount, 2), source).to_converted_dict()


    def get_conversion_info(self, from_currency: str, to_currency: str, amount: float) -> dict:
            conn, cursor = self._get_connection_and_cursor()
            try:
                cursor.execute("""
                    SELECT
                        er.rate,
                        base.id, base.code, base.name, base.sign,
                        target.id, target.code, target.name, target.sign
                    FROM exchange_rates er
                    JOIN currencies base ON er.from_currency = base.code
                    JOIN currencies target ON er.to_currency = target.code
                    WHERE er.from_currency = ? AND er.to_currency = ?
                """, (from_currency.upper(), to_currency.upper()))
                row = cursor.fetchone()

                if not row:
                    raise ExchangeRateNotFoundError(from_currency, to_currency)

                (
                    rate,
                    base_id, base_code, base_name, base_sign,
                    target_id, target_code, target_name, target_sign
                ) = row

                converted_amount = round(rate * amount, 2)

                return {
                    "baseCurrency": currencyDTO(base_id, base_code, base_name, base_sign).to_dict(),
                    "targetCurrency": currencyDTO(target_id, target_code, target_name, target_sign).to_dict(),
                    "rate": rate,
                    "amount": amount,
                    "convertedAmount": converted_amount
                }
            except Exception:
                raise
