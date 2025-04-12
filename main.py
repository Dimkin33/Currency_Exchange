import threading
from model import CurrencyModel
from app_server import start_server

def run_server():
    start_server()

if __name__ == '__main__':
    model = CurrencyModel()
    model.init_db()

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # Устанавливаем поток как фоновый
    server_thread.start()

    print("Сервер запущен в отдельном потоке. Вы можете продолжать работу.")

    # Основной поток может выполнять другие задачи
    while True:
        pass  # Замените на вашу логику, если требуется