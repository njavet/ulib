from pathlib import Path
import importlib
import importlib.util
from sqlalchemy import create_engine

# project imports
from ulib.db import init_db, get_emojis


class UnitManager:
    def __init__(self, db_url) -> None:
        self.engine = create_engine(url=db_url)
        self.cn2proc = {}
        self.cn2cat = {}
        self.emoji2spec = {}
        self.load_categories()
        init_db(self.engine)
        self.load_emojis()

    def load_categories(self, cat_path=Path('ulib', 'categories')):
        for module_path in cat_path.rglob('[a-z]*.py'):
            module_name = module_path.stem
            import_path = '.'.join(cat_path.parts + (module_name,))
            module = importlib.import_module(import_path)
            self.cn2cat[module_name] = module.Category(module_name, self.engine)
            self.cn2proc[module_name] = module.Processor(self.engine)

    def load_emojis(self):
        for emoji_spec in get_emojis(self.engine):
            self.emoji2spec[emoji_spec.base_emoji] = emoji_spec
            self.emoji2spec[emoji_spec.emoji] = emoji_spec

    def process_input(self, timestamp, input_str):
        try:
            emoji, words, comment = self._preprocess_string(input_str)
        except ValueError as err:
            return str(err)

        try:
            emoji_spec = self.emoji2spec[emoji]
        except KeyError:
            return 'Unknown emoji'

        try:
            self.cn2proc[emoji_spec.category_name].process_unit(
                timestamp, words, comment, emoji_spec.key
            )
        except ValueError:
            return 'parsing error'

    @staticmethod
    def _preprocess_string(input_str: str):
        parts = input_str.split('//', 1)
        emoji_payload = parts[0]
        if not emoji_payload:
            raise ValueError('Empty payload')
        if len(parts) > 1 and parts[1]:
            comment = parts[1].strip()
        else:
            comment = None
        all_words = emoji_payload.split()
        emoji = all_words[0]
        words = all_words[1:]
        return emoji, words, comment
