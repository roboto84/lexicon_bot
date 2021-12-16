import logging.config
from .sql_lite_db import SqlLiteDb
from sqlite3 import Connection, Cursor, Error
from typing import Any


class LexiconDb(SqlLiteDb):
    def __init__(self, logging_object: Any, db_location: str):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        super().__init__(logging_object, db_location)
        self._check_db_schema()

    def _check_db_schema(self) -> None:
        if self._check_db_state(['WORDS']):
            self._logger.info(f'DB schema looks good')
        else:
            self._logger.info(f'Tables not found')
            self._create_db_schema()

    def _create_db_schema(self) -> None:
        try:
            conn: Connection = self._db_connect()
            with open('lexicon_bot/bin/db/sql/schema.sql') as f:
                conn.executescript(f.read())
            self._logger.info(f'Initializing Air_DB schema')
            self._db_close(conn)
            self._logger.info(f'Database has been initialized')
        except Error as error:
            self._logger.info(f'Error occurred initializing Air_DB', error)

    def insert_word(self, def_data: dict) -> None:
        word: str = def_data['word']
        sql_path: str = 'lexicon_bot/bin/db/sql/insert_word.sql'
        conn: Connection = self._db_connect()
        db_cursor: Cursor = conn.cursor()
        table_list = db_cursor.execute("""SELECT word FROM WORDS WHERE word=?;""", [word]).fetchall()

        if not table_list:
            try:
                self._logger.info(f'Inserting "{word}" into Lexicon_DB')
                with open(sql_path, 'r') as file:
                    db_cursor.execute(
                        file.read(),
                        (self._get_time(), word.lower(), word, def_data['date_first_used'], def_data['part_of_speech'],
                         def_data['word_break'], def_data['pronounce'], def_data['audio'],
                         str(def_data['etymology']), str(def_data['definitions']), str(def_data['example'])))
            except IOError as e:
                self._logger.info(f'IOError was thrown', e)
            except Exception as e:
                self._logger.exception(f'Exception was thrown', e)
        else:
            self._logger.info(f'"{word}" is already in the DB')
        self._db_close(conn)
