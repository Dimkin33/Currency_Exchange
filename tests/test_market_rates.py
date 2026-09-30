import pytest
import requests

from controller import Controller
from errors import MarketRateProviderError
from market_rates import FrankfurterClient


class FakeResponse:
    def __init__(self, payload, status_error=None):
        self.payload = payload
        self.status_error = status_error

    def raise_for_status(self):
        if self.status_error:
            raise self.status_error

    def json(self):
        return self.payload


def test_frankfurter_client_parses_rate(monkeypatch):
    def fake_get(url, timeout):
        assert url.endswith('/rate/eur/usd')
        assert timeout == 10.0
        return FakeResponse(
            {'date': '2026-09-30', 'base': 'EUR', 'quote': 'USD', 'rate': 1.17}
        )

    monkeypatch.setattr('market_rates.requests.get', fake_get)

    result = FrankfurterClient().get_rate('EUR', 'USD')

    assert result == {
        'provider': 'Frankfurter',
        'date': '2026-09-30',
        'base': 'EUR',
        'quote': 'USD',
        'rate': 1.17,
    }


def test_frankfurter_client_wraps_provider_errors(monkeypatch):
    def fake_get(url, timeout):
        raise requests.Timeout('boom')

    monkeypatch.setattr('market_rates.requests.get', fake_get)

    with pytest.raises(MarketRateProviderError):
        FrankfurterClient().get_rate('EUR', 'USD')


def test_sync_market_rates_upserts_database(monkeypatch):
    values = {'USD': 1.17, 'RUB': 96.36}

    def fake_get_rate(self, base, quote):
        return {
            'provider': 'Frankfurter',
            'date': '2026-09-30',
            'base': base,
            'quote': quote,
            'rate': values[quote],
        }

    monkeypatch.setattr(FrankfurterClient, 'get_rate', fake_get_rate)

    controller = Controller(':memory:')
    result, status = controller.sync_market_rates('EUR', 'USD,RUB')

    assert status == 200
    assert result['provider'] == 'Frankfurter'
    assert result['asOf'] == '2026-09-30'
    assert result['updated'] == 2

    usd_rate, _ = controller.get_exchange_rate('EUR', 'USD')
    rub_rate, _ = controller.get_exchange_rate('EUR', 'RUB')

    assert usd_rate['rate'] == 1.17
    assert rub_rate['rate'] == 96.36

    controller.close()
