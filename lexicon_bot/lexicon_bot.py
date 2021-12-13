# Air data sender
import os
import ast
import logging.config
from typing import Any
from dotenv import load_dotenv
from lexicon.library.lexicon import Lexicon
from bin.lexicon_bot_helper import LexiconBotHelper
from bin.db.lexicon_db import LexiconDb
from wh00t_core.library.client_network import ClientNetwork


class LexiconBot:
    def __init__(self, logging_object: Any, socket_host: str, socket_port: int, webster_key: str, oxford_app_id: str,
                 oxford_key: str, sql_lite_db_path: str):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._chat_key: str = '/lexi '
        self._lexicon: Lexicon = Lexicon(webster_key, oxford_app_id, oxford_key)
        self._lexicon_db = LexiconDb(logging_object, sql_lite_db_path)
        self._socket_network: ClientNetwork = ClientNetwork(socket_host, socket_port, 'lexicon_bot', 'app', logging)

    def run_bot(self) -> None:
        try:
            self._socket_network.sock_it()
            self._socket_network.receive(self._receive_message_callback)
        except KeyboardInterrupt:
            self._logger.info('Received a KeyboardInterrupt... closing bot')
            os._exit(1)

    def _receive_message_callback(self, package: dict) -> bool:
        if ('id' in package) and (package['id'] not in ['wh00t_server', 'lexicon_bot']) and ('message' in package):
            if 'category' in package and package['category'] == 'get_word_definition':
                message_package: dict = ast.literal_eval(package['message'])
                search_word: str = message_package['search_word']
                self._send_api_data(search_word)
            elif 'category' in package and package['category'] == 'chat_message' and \
                    isinstance(package['message'], str) and self._chat_key in package['message']:
                search_word: str = package['message'].replace(self._chat_key, '')
                self._send_chat_data(search_word)
        return True

    def _send_api_data(self, search_word: str) -> None:
        data = self._lexicon.get_dictionary_def(search_word)
        self._socket_network.send_message('word_definition', str(data))
        if LexiconBotHelper.acceptable_def_result_comparator(data):
            self._lexicon_db.insert_word(LexiconBotHelper.parse_dictionary_data(data))

    def _send_chat_data(self, search_word: str):
        self._socket_network.send_message('chat_message', f'Ok, defining "{search_word}" 🤔')
        data = self._lexicon.get_dictionary_def(search_word)

        if LexiconBotHelper.acceptable_def_result_comparator(data):
            data = LexiconBotHelper.parse_dictionary_data(data)
            self._lexicon_db.insert_word(data)
            word_def_chat_message = LexiconBotHelper.chat_message_builder(data)
        elif 'spelling_suggestions' in data and len(data['spelling_suggestions']) > 0:
            word_def_chat_message = 'Looks like the word is misspelled. Perhaps try ...\n\n'
            spell_suggestions = ''.join(f'{spell_suggestion}, ' for spell_suggestion in data['spelling_suggestions'])
            word_def_chat_message = f'{word_def_chat_message}{spell_suggestions}'.rstrip(',')
        else:
            word_def_chat_message = 'Sorry, no information on that word was found.'
        self._socket_network.send_message('chat_message', word_def_chat_message)


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('lexicon_bot/bin/logging.conf'), disable_existing_loggers=False)
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        HOST_SERVER_ADDRESS: str = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT: int = int(os.getenv('SOCKET_SERVER_PORT'))
        MERRIAM_WEBSTER_API_KEY: str = os.getenv('MERRIAM_WEBSTER_API_KEY')
        OXFORD_APP_ID: str = os.getenv('OXFORD_APP_ID')
        OXFORD_APP_KEY: str = os.getenv('OXFORD_APP_KEY')
        SQL_LITE_DB: str = os.getenv('SQL_LITE_DB')

        print(f'\nLexicon data sender will now continuously run')
        lexicon: LexiconBot = LexiconBot(logging, HOST_SERVER_ADDRESS, SOCKET_SERVER_PORT, MERRIAM_WEBSTER_API_KEY,
                                         OXFORD_APP_ID, OXFORD_APP_KEY, SQL_LITE_DB)
        lexicon.run_bot()
    except TypeError:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
