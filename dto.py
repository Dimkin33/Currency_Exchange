from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class requestDTO:
    method: str
    url: str
    headers: Dict[str, Any] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    query_params: Dict[str, Any] = field(default_factory=dict)
    response: Any = None
    status_code: int = None
    
    def to_dict(self):
        return {
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "query_params": self.query_params,
            "response": self.response,
            "status_code": self.status_code
        }
    
    
@dataclass
class currencyDTO:
    id: int = None
    code: str = None
    name: str = None
    sign: str = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "sign": self.sign
        }


@dataclass    
class currencyExchangeDTO:
    id: int = None
    from_currency: str = None
    to_currency: str = None
    rate: float = None

    def to_dict(self):
        return {
            "id": self.id,
            "from_currency": self.from_currency,
            "to_currency": self.to_currency,
            "rate": self.rate
        }

