import os
import json
import pandas as pd
from typing import List, Dict


class SentimentDataLoader:
    """
    Loads individual JSON news sentiment files into a single DataFrame.
    """

    def __init__(self, sentiments_dir: str = "data/sentiments"):
        self.sentiments_dir = sentiments_dir

    def load_all(self) -> pd.DataFrame:
        """Reads all .json files from the sentiment directory and returns a dataframe."""
        records: List[Dict] = []

        for filename in os.listdir(self.sentiments_dir):
            if not filename.endswith(".json"):
                continue

            fpath = os.path.join(self.sentiments_dir, filename)

            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["filename"] = filename     # keep file reference
                    records.append(data)

            except Exception as e:
                print(f"[Loader] Error reading file {filename}: {e}")

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        # Convert dates to datetime
        if "publication_date" in df.columns:
            df["publication_date"] = pd.to_datetime(df["publication_date"], errors="coerce")

        return df
