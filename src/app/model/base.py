import logging
import sqlite3

logger = logging.getLogger(__name__)


class BaseModel:
    def __init__(self, connector: sqlite3.Connection = None):
        self.connector = connector

    def _get_connection_and_cursor(self):
        return self.connector, self.connector.cursor()
