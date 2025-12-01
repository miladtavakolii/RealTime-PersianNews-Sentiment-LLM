import re
from hazm import Normalizer

normalizer = Normalizer()

def clean_text(text: str) -> str:
    if not text:
        return ""

    #remove HTML tags
    text = re.sub(r"<.*?>", " ", text)

    #persian text normilize
    text = normalizer.normalize(text)

    #remove emojies
    text = re.sub(r"[^\w\sآ-ی]", " ", text)

    #remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text
