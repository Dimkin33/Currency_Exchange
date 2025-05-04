import logging
import sqlite3

logger = logging.getLogger(__name__)


class BaseModel:
    """Базовая модель для работы с базой данных SQLite."""

    def __init__(self, connector: sqlite3.Connection = None):
        self.connector = connector

    def _get_connection_and_cursor(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        return self.connector, self.connector.cursor()
