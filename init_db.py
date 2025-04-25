import sqlite3
class Model:
    
    
    
    
    def __init__(self, db_path='currency.db'):
        self.db_path = db_path
        self._use_uri = db_path.startswith("file:")
        
    def _get_connection_and_cursor(self):
        conn = sqlite3.connect(self.db_path, uri = self._use_uri)
        return conn, conn.cursor()

    def init_db(self):

        conn, cursor = self._get_connection_and_cursor()
        print(conn)
        try:
            cursor.execute('''CREATE TABLE IF NOT EXISTS currencies (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                code TEXT UNIQUE,
                                name TEXT,
                                sign TEXT)''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS exchange_rates (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                from_currency TEXT,
                                to_currency TEXT,
                                rate REAL,
                                UNIQUE(from_currency, to_currency))''')
            conn.commit()
        finally:
            conn.close()