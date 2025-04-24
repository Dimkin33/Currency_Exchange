import pytest
from model import CurrencyModel
from errors import CurrencyNotFoundError, ExchangeRateAlreadyExistsError  # noqa: F401

@pytest.fixture()
def model():
    m = CurrencyModel("file:mem1?mode=memory&cache=shared")
    conn, _ = m._get_connection_and_cursor()
    m.init_db()
    yield m
    conn.close()

def test_add_currency(model):
    result = model.add_currency("USD", "US Dollar", "$")
    assert result["code"] == "USD"
    assert result["name"] == "US Dollar"
    assert result["sign"] == "$"

def test_get_currency_by_code(model):
    model.add_currency("USD", "US Dollar", "$")
    result = model.get_currency_by_code("USD")
    assert result["code"] == "USD"

def test_add_exchange_rate(model):
    model.add_currency("USD", "US Dollar", "$")
    model.add_currency("EUR", "Euro", "€")
    result = model.add_exchange_rate("USD", "EUR", 0.9)
    assert result["rate"] == 0.9

def test_exchange_rate_already_exists(model):
    model.add_currency("USD", "US Dollar", "$")
    model.add_currency("EUR", "Euro", "€")
    model.add_exchange_rate("USD", "EUR", 0.9)
    with pytest.raises(ExchangeRateAlreadyExistsError):
        model.add_exchange_rate("USD", "EUR", 1.0)

def test_get_conversion_info_direct(model):
    model.add_currency("USD", "US Dollar", "$")
    model.add_currency("EUR", "Euro", "€")
    model.add_exchange_rate("USD", "EUR", 1.2)
    result = model.get_conversion_info("USD", "EUR", 100)
    assert result["convertedAmount"] == 120.0

def test_get_converted_currency_reverse(model):
    model.add_currency("USD", "US Dollar", "$")
    model.add_currency("EUR", "Euro", "€")
    model.add_exchange_rate("EUR", "USD", 2.0)  # обратный курс
    result = model.get_converted_currency("USD", "EUR", 50)
    assert result["convertedAmount"] == 25.0
    assert result["method"] == "reverse"