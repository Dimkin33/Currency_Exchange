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
                            FOREIGN KEY (from_currency) REFERENCES currencies (id),
                            FOREIGN KEY (to_currency) REFERENCES currencies (id))''')
        conn.commit()
        conn.close()

    def add_currency(self, code, name, sign):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO currencies (code, name, sign) VALUES (?, ?, ?)', (code, *currency_sign.get(code, (None, None))))
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Currency already exists")
        finally:
            conn.close()

    def get_currency_by_code(self, code):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        print(f"Fetching currency with code: {code}")
        cursor.execute('SELECT id, code, name, sign FROM currencies WHERE code = ?', (code,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {'id' : result[0], 'code': result[1], 'name': result[2], 'sign': result[3]  }
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
    
    def get_exchange_rate(self, to_currency, from_currency):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, from_currency, to_currency, rate FROM exchange_rates WHERE from_currency = ? AND to_currency = ?',
                    (from_currency, to_currency))
        result = cursor.fetchone()
        conn.close()
        print(to_currency, from_currency)
        print(f"Result: {result}")
        if result:
            return {'id' : result[0], 'to_currency': result[1], 'from_currency': result[2], 'rate': result[3] }
        else:
            return None
            #значит валютная пара не найдена


    def get_exchange_rates(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM exchange_rates')
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        rates = [dict(zip(columns, row)) for row in rows]
        result = cursor.fetchone()
        conn.close()

        return rates


    def add_exchange_rate(self, from_currency, to_currency, rate):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Проверяем, существует ли уже курс обмена
            cursor.execute('SELECT 1 FROM exchange_rates WHERE from_currency = ? AND to_currency = ?',
                           (from_currency, to_currency))
            if cursor.fetchone():
                raise ValueError("Exchange rate already exists")

            # Если курса нет, добавляем его
            cursor.execute('INSERT INTO exchange_rates (from_currency, to_currency, rate) VALUES (?, ?, ?)',
                           (from_currency, to_currency, rate))
            conn.commit()
            return rate
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
        
