import sqlite3
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv( override=True)

def init_db(connector: sqlite3):
    """Инициализация базы данных.    
    Важно: функция не закрывает переданное подключение,
    это остается ответственностью вызывающего кода."""
    
    cursor = connector.cursor()
    with connector:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS currencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                sign TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchange_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_currency TEXT NOT NULL,
                to_currency TEXT NOT NULL,
                rate REAL NOT NULL,
                UNIQUE(from_currency, to_currency),
                FOREIGN KEY(from_currency) REFERENCES currencies(code) ON DELETE CASCADE,
                FOREIGN KEY(to_currency) REFERENCES currencies(code) ON DELETE CASCADE
            )
        ''')
            

def main():
    # Получаем путь к базе данных из переменной окружения
    db_path = os.getenv('DB_PATH', 'currency.db')  # Если переменная не установлена, будет использован 'currency.db'

    # Устанавливаем соединение с БД
    conn = sqlite3.connect(db_path, uri=True)

    # Инициализируем БД
    init_db(conn)
    print(f"База данных успешно инициализирована по пути: {db_path}")

    # Закрываем соединение
    conn.close()

if __name__ == "__main__":
    main()