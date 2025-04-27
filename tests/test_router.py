import threading
import sqlite3
import time
import socket
import pytest
import requests
from app_server import start_server

BASE_URL = "http://localhost:8000"
global_db_connection = None  # Теперь реально глобальная переменная

def wait_for_server(host, port, timeout=5.0):
    """Проверка, что сервер запущен, используя сокет"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.1)
    raise RuntimeError(f"Server {host}:{port} did not start within {timeout} seconds")


@pytest.fixture(scope="module")
def start_server_fixture():
    """Фикстура для запуска сервера перед тестами"""

    global global_db_connection
    db_path = 'file::memory:?cache=shared'

    # Открываем главное соединение
    global_db_connection = sqlite3.connect(db_path, uri=True)

    def run_server():
        start_server(db_path=db_path)

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    wait_for_server("localhost", 8000)

    yield  # Тут идут тесты

    # После тестов закрываем главное соединение
    global_db_connection.close()
    global_db_connection = None



@pytest.mark.usefixtures("start_server_fixture")
class TestRouter:
    def test_add_currency_usd(self):
        """Добавление валюты USD"""
        payload = {"code": "USD", "name": "US Dollar"}
        response = requests.post(f"{BASE_URL}/currencies", json=payload)
        assert response.status_code == 201
        json_data = response.json()
        assert "id" in json_data
        assert json_data["code"] == "USD"
        assert json_data["name"] == "US Dollar"

    def test_add_currency_eur(self):
        """Добавление валюты EUR"""
        payload = {"code": "EUR", "name": "Euro"}
        response = requests.post(f"{BASE_URL}/currencies", json=payload)
        assert response.status_code == 201
        json_data = response.json()
        assert "id" in json_data
        assert json_data["code"] == "EUR"
        assert json_data["name"] == "Euro"

    def test_get_currencies(self):
        """Тест получения всех валют"""
        response = requests.get(f"{BASE_URL}/currencies")
        assert response.status_code == 200
        json_data = response.json()
        assert isinstance(json_data, list)
        codes = [currency["code"] for currency in json_data]
        assert "USD" in codes
        assert "EUR" in codes

    def test_get_currency_by_code(self):
        """Тест получения валюты по коду"""
        params = {"code": "USD"}
        response = requests.get(f"{BASE_URL}/currency", params=params)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["code"] == "USD"
        assert json_data["name"] == "US Dollar"

    def test_add_exchange_rate(self):
        """Добавление курса обмена USD -> EUR"""
        payload = {"from": "USD", "to": "EUR", "rate": 0.85}
        response = requests.post(f"{BASE_URL}/exchangeRates", json=payload)
        assert response.status_code == 201
        json_data = response.json()
        assert "id" in json_data
        assert json_data["from_currency"] == "USD"
        assert json_data["to_currency"] == "EUR"
        assert json_data["rate"] == 0.85

    def test_get_exchange_rate(self):
        """Тест получения курса обмена"""
        params = {"from": "USD", "to": "EUR"}
        response = requests.get(f"{BASE_URL}/exchangeRate", params=params)
        assert response.status_code == 200
        json_data = response.json()
        assert "rate" in json_data
        assert json_data["rate"] == 0.85

    def test_convert_currency(self):
        """Тест конвертации валюты"""
        params = {"from": "USD", "to": "EUR", "amount": 100}
        response = requests.get(f"{BASE_URL}/convert", params=params)
        assert response.status_code == 200
        json_data = response.json()
        assert "convertedAmount" in json_data
        assert json_data["convertedAmount"] == 85.0

    def test_delete_all_currencies(self):
        """Тест очистки всех валют и курсов"""
        response = requests.post(f"{BASE_URL}/currencies/delete_all")
        assert response.status_code == 200
        json_data = response.json()
        assert "message" in json_data
        assert json_data["message"] == "All currencies and exchange rates deleted, ids reset"

    def test_get_currencies_after_delete(self):
        """Тест проверки отсутствия валют после удаления"""
        response = requests.get(f"{BASE_URL}/currencies")
        assert response.status_code == 200
        json_data = response.json()
        assert isinstance(json_data, list)
        assert len(json_data) == 0
