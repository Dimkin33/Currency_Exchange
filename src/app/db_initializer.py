import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


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
    load_dotenv()
    db_path = os.getenv("DB_PATH", "db/currency.db")
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)  # создаём папки, если не существуют

    conn = sqlite3.connect(db_path, uri=True)
    init_db(conn)
    print(f"База данных успешно инициализирована по пути: {db_path}")
    conn.close()

if __name__ == "__main__":
    main()
