import json
import os


def write_last_timestamp(spider_name: str, timestamp: int, meta_dir: str = 'meta') -> None:
    '''
    Write the timestamp to the meta directory.

    Args:
        spider_name: The name of the spider for which the timestamp is being set
        timestamp: The timestamp value to be saved
        meta_dir: Directory to save the timestamp file
    '''
    if not os.path.exists(meta_dir):
        os.makedirs(meta_dir)

    file_path = f'{meta_dir}/{spider_name}_last.json'

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({'last_timestamp': timestamp},
                  f, ensure_ascii=False, indent=4)

    print(
        f'[Timestamp] Written timestamp {timestamp} for {spider_name} in {file_path}')

def write_real_last_timestamp(spider_name: str, timestamp: int, meta_dir: str = 'meta') -> None:
    '''
    Write the timestamp to the meta directory only if newer.

    Args:
        spider_name: The name of the spider for which the timestamp is being set
        timestamp: The timestamp value to be saved
        meta_dir: Directory to save the timestamp file
    '''
    file_path = f'{meta_dir}/{spider_name}_last.json'

    with open(file_path, 'r', encoding='utf-8') as f:
        file_timestamp = json.loads(f.read())['last_timestamp']
        if int(file_timestamp) < timestamp:
            write_last_timestamp(spider_name, timestamp, meta_dir)
