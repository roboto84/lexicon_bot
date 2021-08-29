# Air data sender
import os
import ast
import logging.config
from typing import Any
from dotenv import load_dotenv
from lexicon.library.lexicon import Lexicon
from wh00t_core.library.client_network import ClientNetwork


class LexiconBot:
    def __init__(self, logging_object: Any, socket_host: str, socket_port: int, webster_key: str, oxford_app_id: str,
                 oxford_key: str):
        self.logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)
        self.lexicon: Lexicon = Lexicon(webster_key, oxford_app_id, oxford_key)
        self.socket_network: ClientNetwork = ClientNetwork(socket_host, socket_port,
                                                           'lexicon_bot', 'app', logging)

    def run_bot(self) -> None:
        self.socket_network.sock_it()
        self.socket_network.receive(self.__receive_message_callback)

    def __receive_message_callback(self, package: dict) -> bool:
        if package['id'] not in ['wh00t_server', 'lexicon_bot'] and 'category' in package \
                and package['category'] == 'get_word_definition' and 'message' in package:
            message: dict = ast.literal_eval(package['message'])
            search_word: str = message['search_word']
            self.__send_dictionary_data(search_word)
        return True

    def __send_dictionary_data(self, search_word) -> None:
        dictionary_payload: dict = self.get_data(search_word)
        self.socket_network.send_message('word_definition', str(dictionary_payload))

    def get_data(self, search_word: str) -> dict:
        return self.lexicon.get_dictionary_def(search_word)


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

        print(f'\nLexicon data sender will now continuously run')
        lexicon: LexiconBot = LexiconBot(logging, HOST_SERVER_ADDRESS, SOCKET_SERVER_PORT, MERRIAM_WEBSTER_API_KEY,
                                         OXFORD_APP_ID, OXFORD_APP_KEY)
        lexicon.run_bot()
    except TypeError:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
