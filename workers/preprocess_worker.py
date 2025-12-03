import os
import json
from utils.rabbitmq import RabbitMQClient
from preprocessing.clean_text import TextCleaner
from typing import Any, Dict


class PreprocessWorker:
    '''
    Class responsible for processing and cleaning news articles from a RabbitMQ queue.

    It listens to an input queue, cleans the articles, saves them to files, 
    and sends them to an output queue.
    '''

    def __init__(self, input_queue: str = 'raw_news', output_queue: str = 'clean_news', out_dir: str = 'data/cleaned'):
        '''
        Initializes the PreprocessWorker with input and output queues and an output directory.

        Args:
            input_queue: The name of the input queue from which messages are consumed.
            output_queue: The name of the output queue where processed articles are sent.
            out_dir: The directory where cleaned articles are saved as JSON files.
        '''
        self.input_queue: str = input_queue
        self.output_queue: str = output_queue
        self.out_dir: str = out_dir

        # Ensure output directory exists
        os.makedirs(self.out_dir, exist_ok=True)

        # Singleton RabbitMQ client
        self.rabbit = RabbitMQClient()

        # Declare queues (idempotent)
        self.rabbit.declare_queue(self.input_queue)
        self.rabbit.declare_queue(self.output_queue)

        # Text cleaner instance
        self.text_cleaner = TextCleaner()

    def handle_message(self, ch: Any, method: Any, props: Any, article: Dict[str, Any]) -> None:
        '''
        Processes a single message from the input queue, cleans the article, saves it,
        and publishes it to the output queue.

        Args:
            ch (Any): The channel object from RabbitMQ.
            method (Any): The method associated with the message.
            props (Any): The properties associated with the message.
            article (Dict[str, Any]): The article dictionary containing raw data to be cleaned.
        '''
        # Clean text fields
        article['title'] = self.text_cleaner.clean(article['title'])
        article['content'] = self.text_cleaner.clean(article['content'])
        article['summary'] = self.text_cleaner.clean(article['summary'])

        # Save cleaned file locally
        self._save_to_file(article)

        # Send cleaned message to next queue
        self.rabbit.publish(self.output_queue, article)

        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _save_to_file(self, article: Dict[str, Any]) -> None:
        '''
        Saves the cleaned article to a JSON file in the output directory.

        Args:
            article (Dict[str, Any]): The cleaned article to be saved.
        '''
        filename: str = article['raw_filename']
        filepath: str = os.path.join(self.out_dir, f'{filename}.json')
        del article['raw_filename']  # Remove raw filename before saving

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)

    def start(self) -> None:
        '''
        Starts consuming messages from the input queue.

        This method listens to the input queue and processes each message using 
        the handle_message callback function.
        '''
        print(f'[PreprocessWorker] Listening on queue: {self.input_queue}')
        self.rabbit.consume(self.input_queue, callback=self.handle_message)
