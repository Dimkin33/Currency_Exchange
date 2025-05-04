import os
import sqlite3

import pytest
from db_initializer import init_db
from dotenv import load_dotenv
from errors import CurrencyAlreadyExistsError
from model import CurrencyModel

# Загрузка переменных окружения из .env
load_dotenv()


@pytest.fixture()
def model():
    """Создает ин-мемори базу данных и модель для тестов"""
    db_path = os.getenv('TEST_DB_PATH', ':memory:')  # Получаем путь к базе из .env
    conn = sqlite3.connect(db_path, uri=True)  # Создаем подключение к базе данных
    init_db(conn)  # 🔥 Инициализация схемы через db_initializer
    yield CurrencyModel(conn)
    conn.close()


@pytest.mark.parametrize(
    'code, name, sign',
    [
        ('USD', 'Dollar', '$'),
        ('EUR', 'Euro', '€'),
        ('JPY', 'Yen', '¥'),
    ],
)
def test_add_currency(model, code, name, sign):
    """Проверяем добавление разных валют"""
    result = model.add_currency(code, name, sign)
    assert result['code'] == code
    assert result['name'] == name
    assert result['sign'] == sign


def test_add_duplicate_currency(model):
    """Проверяем ошибку при добавлении валюты с тем же кодом"""
    code, name, sign = 'USD', 'Dollar', '$'
    model.add_currency(code, name, sign)

    with pytest.raises(CurrencyAlreadyExistsError):
        model.add_currency(code, 'US Dollar', '$$')
