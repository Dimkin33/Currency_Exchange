import logging
import threading

from app_server import start_server

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Устанавливаем уровень DEBUG
    format='%(asctime)s - %(name)-11s -%(funcName)-22s- %(levelname)-8s - %(message)-s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),  # Логи в файл
        logging.StreamHandler(),  # Логи в консоль
    ],
)


def run_server():
    start_server()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info('Запуск сервера в отдельном потоке')
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True  # Устанавливаем поток как фоновый
    server_thread.start()

    logger.info('Сервер запущен. Ожидание запросов.')

    # Основной поток может выполнять другие задачи
    try:
        while True:
            pass  # Замените на вашу логику, если требуется
    except KeyboardInterrupt:
        logger.info('Завершение работы сервера')
