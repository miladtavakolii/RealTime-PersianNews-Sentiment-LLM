import re
from hazm import Normalizer


class TextCleaner:
    '''
    A modular and extensible Persian text cleaner.

    This class provides utilities for cleaning Persian text, including:
        - Removing HTML tags
        - Normalizing Persian text (using a Normalizer instance)
        - Removing emojis and non-Persian characters
        - Removing extra spaces

    The class is designed to precompile regex patterns and initialize heavy modules once,
    making repeated text cleaning efficient.
    '''

    def __init__(self) -> None:
        '''
        Initialize the TextCleaner.

        Sets up the Persian text normalizer and precompiles regular expressions
        for HTML tags, emojis/non-Persian characters, and extra spaces.
        '''
        # Initialize heavy modules one time only
        self.normalizer = Normalizer()

        # Precompile regex patterns (faster)
        self.html_pattern = re.compile(r'<.*?>')
        self.emoji_pattern = re.compile(r'[^\w\sآ-ی]')
        self.space_pattern = re.compile(r'\s+')

    def clean(self, text: str) -> str:
        '''
        Clean the input Persian text.

        Steps performed:
            1. Remove HTML tags.
            2. Normalize Persian text.
            3. Remove emojis and non-Persian characters.
            4. Collapse multiple spaces into a single space and strip leading/trailing spaces.

        Args:
            text: The input Persian text to clean.

        Returns:
            The cleaned Persian text. Returns an empty string if the input is None or empty.
        '''
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
