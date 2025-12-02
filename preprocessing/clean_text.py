import re
from hazm import Normalizer


class TextCleaner:
    '''A modular and extensible Persian text cleaner.'''

    def __init__(self):
        # Initialize heavy modules one time only
        self.normalizer = Normalizer()

        # Precompile regex patterns (faster)
        self.html_pattern = re.compile(r'<.*?>')
        self.emoji_pattern = re.compile(r'[^\w\sآ-ی]')
        self.space_pattern = re.compile(r'\s+')

    def clean(self, text: str) -> str:
        '''Clean the input Persian text.'''
        if not text:
            return ''

        # Remove HTML tags
        text = self.html_pattern.sub(' ', text)

        # Normalize Persian text
        text = self.normalizer.normalize(text)

        # Remove emojis & non-Persian characters
        text = self.emoji_pattern.sub(' ', text)

        # Remove extra spaces
        text = self.space_pattern.sub(' ', text).strip()

        return text
