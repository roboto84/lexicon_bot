
class LexiconBotUtils:
    @staticmethod
    def lexicon_help_message() -> str:
        return f'  🤔\n\nDoesn\'t look like you gave me a word to lookup ...\n' \
               f'"/lexi" dictionary commands are as follows:\n\n' \
               f'     /lexi {{word_to_define}} : gives dictionary data on word_to_define\n'
