import sqlite3
from sign_code import currency_sign

class CurrencyModel:
    def __init__(self, db_path='currency.db'):
        self.db_path = db_path

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS currencies (
                            code TEXT PRIMARY KEY,
                            name TEXT NOT NULL,
                            sign TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS exchange_rates (
                            from_currency TEXT,
                            to_currency TEXT,
                            rate REAL,
                            PRIMARY KEY (from_currency, to_currency),
                            FOREIGN KEY (from_currency) REFERENCES currencies (code),
                            FOREIGN KEY (to_currency) REFERENCES currencies (code))''')
        conn.commit()
        conn.close()

    def get_currency_by_code(self, code):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        print(f"Fetching currency with code: {code}")
        cursor.execute('SELECT code, name, sign FROM currencies WHERE code = ?', (code,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {'code': result[0], 'name': result[1], 'sign': result[2] }
        else:
            return None
    
    def get_currencies(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT code, name, sign FROM currencies')
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        currencies = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return currencies

    def add_currency(self, code, name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO currencies (code, name, sign) VALUES (?, ?, ?)', (code, *currency_sign.get(code, (None, None))))
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Currency already exists")
        finally:
            conn.close()

    def get_exchange_rates(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM exchange_rates')
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        rates = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return rates

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

    def convert_currency(self, from_currency, to_currency, amount):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT rate FROM exchange_rates WHERE from_currency = ? AND to_currency = ?',
                       (from_currency, to_currency))
        result = cursor.fetchone()
        conn.close()
        if result:
            rate = result[0]
            return amount * rate
        else:
            raise ValueError("Exchange rate not found")