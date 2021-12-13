

class LexiconBotHelper:
    @staticmethod
    def acceptable_def_result_comparator(data: dict) -> bool:
        webster_def_is_good = ('state' in data['merriam_webster'] and data['merriam_webster']['state'] != 'unavailable')
        oxford_def_is_good = ('state' in data['oxford'] and data['oxford']['state'] != 'unavailable')
        return webster_def_is_good or oxford_def_is_good

    @staticmethod
    def chat_message_builder(data: dict) -> str:
        definition_string: str = ''.join(f'◦ {single_def}\n' for single_def in data['definitions'])

        return f'\n📚  {data["word"].capitalize()} | {data["date_first_used"]} {data["part_of_speech"]}, ' \
               f'{data["word_break"]} \\ {data["pronounce"]} \n' \
               f'{data["audio"]} \n\n' \
               f'etymology | {data["etymology"]} \n\n' \
               f'{definition_string} \n' \
               f'( ex | {data["example"].capitalize()} )'

    @staticmethod
    def parse_dictionary_data(data: dict) -> dict:
        date_first_used: str = ''
        part_of_speech: str = ''
        word_break: str = ''
        pronounce: str = ''
        audio: str = ''
        etymology: str = ''
        definitions: list[str] = []
        example: str = ''

        if 'merriam_webster' in data:
            mw = data['merriam_webster']
            date_first_used = mw['date_first_used'] if ('date_first_used' in mw) else 'unk'
            part_of_speech = mw['part_of_speech'] if ('part_of_speech' in mw) else 'unk'
            word_break = mw['word_break'] if ('word_break' in mw) else 'unk'
            pronounce = mw['pronounce'] if ('pronounce' in mw) else 'unk'
            etymology = mw['etymology'] if ('etymology' in mw) else 'unk'
            if 'definition' in mw and len(mw['definition']) > 0:
                definitions = mw['definition']

        if 'oxford' in data:
            ox = data['oxford']
            audio = ox['audio'] if ('audio' in ox) else 'unk'
            example = ox['example'] if ('example' in ox) else 'unk'
            if 'definition' in ox and len(ox['definition']) > 0:
                definitions = definitions + ox['definition']

        return {
            'word': data["search_word"],
            'date_first_used': date_first_used,
            'part_of_speech': part_of_speech,
            'word_break': word_break,
            'pronounce': pronounce,
            'audio': audio,
            'etymology': etymology,
            'definitions': definitions,
            'example': example
        }
