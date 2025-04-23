from dataclasses import dataclass

@dataclass
class currencyDTO:
    id: int
    code: str
    name: str
    sign: str

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "sign": self.sign
        }

@dataclass
class currencyExchangeDTO:
    id: int
    from_currency: dict
    to_currency: dict
    rate: float
    amount: float = None
    convertedAmount: float = None
    method: str = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "baseCurrency": self.from_currency,
            "targetCurrency": self.to_currency,
            "rate": self.rate
        }

       
    def to_converted_dict(self):
        return {
            "baseCurrency": self.from_currency,
            "targetCurrency": self.to_currency,
            "rate": self.rate,
            "amount": self.amount,
            "convertedAmount": self.convertedAmount,
            "method": self.method
        }
