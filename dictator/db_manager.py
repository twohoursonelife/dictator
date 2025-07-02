import mysql.connector
from dictator.constants import DB_DATABASE, DB_HOST, DB_PASSWORD, DB_USER


class db_connection:
    def __init__(self):
        self.db = mysql.connector.connect(
            host=DB_HOST,
            database=DB_DATABASE,
            user=DB_USER,
            password=DB_PASSWORD,
            autocommit=True,
        )

        self.cursor = self.db.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
            self.db.close()
