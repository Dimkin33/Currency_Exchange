import sqlite3

import pytest
from db_initializer import init_db
from errors import CurrencyAlreadyExistsError
from model import CurrencyModel


@pytest.fixture()
def model():
    """Создает ин-мемори базу данных и модель для тестов"""
    conn = sqlite3.connect(":memory:")
    init_db(conn)  # 🔥 Инициализация схемы через твой db_initializer
    yield CurrencyModel(conn)
    conn.close()


@pytest.mark.parametrize("code, name, sign", [
    ("USD", "Dollar", "$"),
    ("EUR", "Euro", "€"),
    ("JPY", "Yen", "¥"),
])
def test_add_currency(model, code, name, sign):
    """Проверяем добавление разных валют"""
    result = model.add_currency(code, name, sign)
    assert result['code'] == code
    assert result['name'] == name
    assert result['sign'] == sign


def test_add_duplicate_currency(model):
    """Проверяем ошибку при добавлении валюты с тем же кодом"""
    code, name, sign = "USD", "Dollar", "$"
    model.add_currency(code, name, sign)

    with pytest.raises(CurrencyAlreadyExistsError):
        model.add_currency(code, "US Dollar", "$$")
