import os

import requests

from errors import MarketRateProviderError


class FrankfurterClient:
    """Small client for the public Frankfurter v2 exchange-rate API."""

    provider_name = 'Frankfurter'

    def __init__(self, base_url: str = None, timeout: float = 10.0):
        self.base_url = (
            base_url
            or os.getenv('MARKET_API_URL', 'https://api.frankfurter.dev/v2')
        ).rstrip('/')
        self.timeout = timeout

    def get_rate(self, base: str, quote: str) -> dict:
        base = base.upper()
        quote = quote.upper()

        if base == quote:
            return {
                'provider': self.provider_name,
                'date': None,
                'base': base,
                'quote': quote,
                'rate': 1.0,
            }

        url = f'{self.base_url}/rate/{base.lower()}/{quote.lower()}'

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise MarketRateProviderError(
                f'Unable to fetch {base}/{quote} from {self.provider_name}'
            ) from exc

        try:
            rate = float(payload['rate'])
        except (KeyError, TypeError, ValueError) as exc:
            raise MarketRateProviderError(
                f'Invalid {self.provider_name} response for {base}/{quote}'
            ) from exc

        return {
            'provider': self.provider_name,
            'date': payload.get('date'),
            'base': str(payload.get('base', base)).upper(),
            'quote': str(payload.get('quote', quote)).upper(),
            'rate': rate,
        }
