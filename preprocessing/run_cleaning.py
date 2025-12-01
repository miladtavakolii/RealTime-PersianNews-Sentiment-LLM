import pandas as pd
from clean_text import clean_text


def run_cleaning(read_path: str, write_path: str):
    df = pd.read_json(read_path)

    df["content"] = df["content"].apply(clean_text)
    df["title"] = df["title"].apply(clean_text)
    df["summary"] = df["summary"].apply(clean_text)

    df.to_json(write_path, orient="records")
