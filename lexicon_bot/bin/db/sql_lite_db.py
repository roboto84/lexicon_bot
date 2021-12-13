
import logging.config
import sqlite3
from datetime import datetime
from sqlite3 import Connection, Cursor
from typing import Any, Callable


class SqlLiteDb:
    def __init__(self, logging_object: Any, db_location: str):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._db_location: str = db_location

    @staticmethod
    def _check_table_exists(db_cursor: Cursor, table_name: str) -> bool:
        table_list = db_cursor.execute(
            """SELECT tbl_name FROM sqlite_master WHERE type='table' AND tbl_name=?;""", [table_name]).fetchall()
        if table_list:
            return True
        return False

    @staticmethod
    def _get_time() -> str:
        return datetime.now().strftime('%m/%d/%Y-%H:%M:%S')

    def _db_connect(self) -> Connection:
        conn: Connection = sqlite3.connect(self._db_location)
        self._logger.info(f'Opened DB "{self._db_location}" successfully')
        return conn

    def _db_close(self, live_db_connection: Connection) -> None:
        live_db_connection.commit()
        live_db_connection.close()
        self._logger.info(f'Saved and Closed DB "{self._db_location}" successfully')

    def _check_db_state(self, table_names: list[str], create_db_schema: Callable[[Cursor], None]) -> None:
        conn: Connection = self._db_connect()
        db_cursor: Cursor = conn.cursor()
        db_schema_good: bool = True
        for table_name in table_names:
            db_schema_good = db_schema_good and self._check_table_exists(db_cursor, table_name)

        if db_schema_good:
            self._logger.info(f'DB schema looks good')
        else:
            self._logger.info(f'Tables not found, generating DB schema')
            create_db_schema(db_cursor)
            self._logger.info(f'Tables have been created')
        self._db_close(conn)
