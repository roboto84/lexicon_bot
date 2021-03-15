# Air data sender
import os
import ast
import logging.config
from typing import Any, NoReturn
from dotenv import load_dotenv
from lexicon.library.lexicon import Lexicon
from wh00t_core.library.client_network import ClientNetwork


class LexiconBot:
    def __init__(self, logging_object: Any, socket_host: str, socket_port: int, webster_key: str, oxford_app_id: str,
                 oxford_key: str):
        self.logger: Any = logging_object.getLogger(type(self).__name__)
        self.logger.setLevel(logging.INFO)
        self.socket_host: str = socket_host
        self.socket_port: int = socket_port
        self.receive_thread: Any = None
        self.lexicon = Lexicon(webster_key, oxford_app_id, oxford_key)
        self.socket_network: ClientNetwork = ClientNetwork(self.socket_host, self.socket_port,
                                                           'lexicon_bot', 'app', logging)

    def run_bot(self) -> NoReturn:
        self.socket_network.sock_it()
        self.socket_network.receive(self.__receive_message_callback)

    def __receive_message_callback(self, package) -> NoReturn:
        print(package)
        if package['id'] not in ['wh00t_server', 'lexicon_bot'] and 'category' in package \
                and package['category'] == 'get_word_definition' and 'message' in package:
            message: dict = ast.literal_eval(package['message'])
            print(message)
            search_word = message['search_word']
            print(search_word)
            self.__send_dictionary_data(search_word)

    def __send_dictionary_data(self, search_word) -> NoReturn:
        dictionary_payload = self.get_data(search_word)
        print(dictionary_payload)
        self.socket_network.send_message('word_definition', str(dictionary_payload['oxford']))

    def get_data(self, search_word: str) -> dict:
        return self.lexicon.get_dictionary_def(search_word)


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('lexicon_bot/bin/logging.conf'), disable_existing_loggers=False)
    logger: Any = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        HOST_SERVER_ADDRESS: str = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT: int = int(os.getenv('SOCKET_SERVER_PORT'))
        MERRIAM_WEBSTER_API_KEY: str = os.getenv('MERRIAM_WEBSTER_API_KEY')
        OXFORD_APP_ID: str = os.getenv('OXFORD_APP_ID')
        OXFORD_APP_KEY: str = os.getenv('OXFORD_APP_KEY')

        print(f'\nLexicon data sender will now continuously run')
        lexicon = LexiconBot(logging, HOST_SERVER_ADDRESS, SOCKET_SERVER_PORT, MERRIAM_WEBSTER_API_KEY,
                             OXFORD_APP_ID, OXFORD_APP_KEY)
        lexicon.run_bot()
    except TypeError:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
