import sqlite3
from sign_code import currency_sign

class CurrencyModel:
    def __init__(self, db_path='currency.db'):
        self.db_path = db_path

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS currencies (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            code TEXT NOT NULL UNIQUE,
                            name TEXT NOT NULL,
                            sign TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS exchange_rates (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            from_currency TEXT,
                            to_currency TEXT,
                            rate REAL,
                            FOREIGN KEY (from_currency) REFERENCES currencies (code),
                            FOREIGN KEY (to_currency) REFERENCES currencies (code))''')
        conn.commit()
        conn.close()

    def add_currency(self, code, name, sign):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO currencies (code, name, sign) VALUES (?, ?, ?)', (code, name, sign))
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Currency already exists")
        finally:
            conn.close()

    def get_currency_by_code(self, code):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT code, name, sign FROM currencies WHERE code = ?', (code,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {"code": result[0], "name": result[1], "sign": result[2]}
        return None

    def get_currencies(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT code, name, sign FROM currencies')
        rows = cursor.fetchall()
        conn.close()
        return [{"code": row[0], "name": row[1], "sign": row[2]} for row in rows]

    def add_exchange_rate(self, from_currency, to_currency, rate):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO exchange_rates (from_currency, to_currency, rate) VALUES (?, ?, ?)',
                           (from_currency, to_currency, rate))
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Exchange rate already exists")
        finally:
            conn.close()

    def get_exchange_rates(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT from_currency, to_currency, rate FROM exchange_rates')
        rows = cursor.fetchall()
        conn.close()
        return [{"from": row[0], "to": row[1], "rate": row[2]} for row in rows]

    def convert_currency(self, from_currency, to_currency, amount):
        rates = self.get_exchange_rates()
        rate = next((r['rate'] for r in rates if r['from'] == from_currency and r['to'] == to_currency), None)
        if rate is None:
            raise ValueError("Exchange rate not found")
        return amount * rate

    def get_exchange_rate(self, from_currency, to_currency):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT rate FROM exchange_rates WHERE from_currency = ? AND to_currency = ?', (from_currency, to_currency))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {"from": from_currency, "to": to_currency, "rate": result[0]}
        return None

