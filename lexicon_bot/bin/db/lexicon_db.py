import logging.config
from .sql_lite_db import SqlLiteDb
from .db_schema import create_table_words
from sqlite3 import Connection, Cursor
from typing import Any


class LexiconDb(SqlLiteDb):
    def __init__(self, logging_object: Any, db_location: str):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        super().__init__(logging_object, db_location)
        self._check_db_schema()

    def _check_db_schema(self) -> None:
        self._check_db_state(['WORDS'], self._create_db_schema)

    @staticmethod
    def _create_db_schema(db_cursor: Cursor) -> None:
        db_cursor.execute(create_table_words)

    def insert_word(self, def_data: dict) -> None:
        word: str = def_data['word']
        conn: Connection = self._db_connect()
        db_cursor: Cursor = conn.cursor()
        table_list = db_cursor.execute("""SELECT word FROM WORDS WHERE word=?;""", [word]).fetchall()

        if not table_list:
            self._logger.info(f'Inserting "{word}" into Lexicon_DB')
            db_cursor.execute(
                """INSERT INTO words(time, word, word_letter_cased, date_first_used, part_of_speech, word_break, 
                pronounce, audio, etymology, definitions, example) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                (self._get_time(), word.lower(), word, def_data['date_first_used'], def_data['part_of_speech'],
                 def_data['word_break'], def_data['pronounce'], def_data['audio'],
                 str(def_data['etymology']), str(def_data['definitions']), str(def_data['example'])))
        else:
            self._logger.info(f'"{word}" is already in the DB')
        self._db_close(conn)
