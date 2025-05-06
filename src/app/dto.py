from dataclasses import dataclass


@dataclass
class CurrencyDTO:
    """Currency data transfer object"""

    id: int
    code: str
    name: str
    sign: str

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {'id': self.id, 'code': self.code, 'name': self.name, 'sign': self.sign}


@dataclass
class CurrencyExchangeDTO:
    """Exchange rate data transfer object"""

    id: int
    from_currency: CurrencyDTO
    to_currency: CurrencyDTO
    rate: float
    amount: float = None
    convertedAmount: float = None
    method: str = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'baseCurrency': self.from_currency,
            'targetCurrency': self.to_currency,
            'rate': self.rate,
        }

    def to_converted_dict(self) -> dict:
        """Convert to dictionary representation for conversion"""
        return {
            'baseCurrency': self.from_currency,
            'targetCurrency': self.to_currency,
            'rate': self.rate,
            'amount': self.amount,
            'convertedAmount': self.convertedAmount,
            'method': self.method,
        }
