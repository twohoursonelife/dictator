import mysql.connector
from dictator.settings import config


class db_connection:
    def __init__(self):
        self.db = mysql.connector.connect(
            host=config.DB_HOST,
            database=config.DB_DATABASE,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            autocommit=True,
        )

        self.cursor = self.db.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
            self.db.close()
