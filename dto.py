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
