import os
import json
import pandas as pd
from typing import List, Dict


class SentimentDataLoader:
    '''
    Loader class for sentiment-analyzed news articles stored as JSON files.

    This class reads all JSON files from a specified directory, extracts their contents,
    and returns a unified Pandas DataFrame. Each row represents a single article enriched
    with sentiment information.

    Attributes:
        sentiments_dir (str):
            Directory path containing JSON files of sentiment-analyzed articles.
    '''

    def __init__(self, sentiments_dir: str = 'data/sentiments'):
        '''
        Initialize the loader with the directory containing sentiment JSON files.

        Args:
            sentiments_dir (str, optional):
                Path to the directory containing JSON files.
                Defaults to 'data/sentiments'.
        '''
        self.sentiments_dir = sentiments_dir

    def load_all(self) -> pd.DataFrame:
        '''
        Load all sentiment JSON files into a single Pandas DataFrame.

        Processing steps:
            1. Iterates through all `.json` files in the `sentiments_dir`.
            2. Reads each file as a dictionary and keeps the original filename as a reference.
            3. Aggregates all records into a list.
            4. Converts the list of dictionaries into a Pandas DataFrame.
            5. Converts the 'publication_date' column to datetime (if present).

        Returns:
            pd.DataFrame:
                DataFrame containing all loaded articles with sentiment data.
                Returns an empty DataFrame if no files are found or an error occurs.
        '''
        records: List[Dict] = []

        for filename in os.listdir(self.sentiments_dir):
            if not filename.endswith('.json'):
                continue

            fpath = os.path.join(self.sentiments_dir, filename)

            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['filename'] = filename     # keep file reference
                    records.append(data)

            except Exception as e:
                print(f'[Loader] Error reading file {filename}: {e}')

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        # Convert dates to datetime
        if 'publication_date' in df.columns:
            df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')

        return df
