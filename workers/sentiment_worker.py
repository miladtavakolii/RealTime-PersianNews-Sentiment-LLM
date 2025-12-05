import os
import json
from typing import Any, Dict

from utils.rabbitmq import RabbitMQClient
from sentiment_engine.engine import SentimentEngine
from sentiment_engine.ollama_client import OllamaClient
from sentiment_engine.gemini_client import GeminiClient
from sentiment_engine.base import BaseSentimentProvider
from scheduler.write_last_timestamp import write_last_timestamp


class SentimentWorker:
    '''
    Worker component responsible for performing sentiment analysis on cleaned news articles.

    This worker:
        - Consumes cleaned articles from a RabbitMQ queue
        - Runs sentiment analysis using a configurable LLM provider
        - Saves the enriched output to local storage
        - Optionally publishes results to a downstream queue
        - Updates the last-processed timestamp for each website

    Attributes:
        input_queue:
            Name of the queue from which cleaned articles are consumed.
        output_queue:
            Name of the queue where sentiment-enriched articles may be published.
        out_dir:
            Directory where processed articles are saved.
        rabbit:
            Shared RabbitMQ client for message operations.
        engine:
            High-level LLM sentiment engine performing text analysis.
    '''

    def __init__(self, model_info: dict, input_queue: str = 'clean_news', output_queue: str = 'sentiment_news', out_dir: str = 'data/sentiments'):
        '''
        Initialize the SentimentWorker and its underlying components.

        Args:
            model_info:
                Model configuration dictionary containing at least:
                    - 'name': The LLM model name
                    - 'prompt_template_path': Path to the prompt template file
            input_queue:
                Queue name from which cleaned news articles are consumed.
            output_queue :
                Queue name to publish sentiment results to.
            out_dir:
                Directory where enriched article JSON files will be saved.

        Raises:
            FileNotFoundError:
                If the prompt template file does not exist.
        '''
        self.input_queue: str = input_queue
        self.output_queue: str = output_queue
        self.out_dir: str = out_dir

        os.makedirs(self.out_dir, exist_ok=True)

        # Singleton RabbitMQ client
        self.rabbit = RabbitMQClient()

        # Declare queues (idempotent)
        self.rabbit.declare_queue(self.input_queue)
        self.rabbit.declare_queue(self.output_queue)

        # INIT SENTIMENT ENGINE
        prompt_template = open(model_info['prompt_template_path']).read()
        if model_info['provider'] == 'ollama':
            provider: BaseSentimentProvider = OllamaClient(
                model=model_info['name'], prompt_template=prompt_template)

        elif model_info['provider'] == 'gemini':
            provider: BaseSentimentProvider = GeminiClient(
                model=model_info['name'], prompt_template=prompt_template)

        self.engine = SentimentEngine(provider=provider)

    def handle_message(self, ch: Any, method: Any, props: Any, article: Dict[str, Any]) -> None:
        '''
        Process a single cleaned article from RabbitMQ.

        Steps:
            1. Perform sentiment analysis using the LLM engine
            2. Attach sentiment results to the article object
            3. Save the enriched article locally
            4. Update the last processed timestamp for the article's website
            5. Acknowledge the message in RabbitMQ

        Args:
            ch: RabbitMQ channel object for acknowledgment.
            method: Message delivery method (contains delivery tag).
            props: Message properties.
            article: Article data containing title, summary, content, metadata, etc.

        Raises:
            ValueError:
                If the sentiment engine produces invalid JSON.
        '''
        sentiment_result = self.engine.analyze(
            title=article.get('title', ''),
            publication_date=article.get('publication_date', ''),
            summary=article.get('summary', ''),
            content=article.get('content', ''),
            categories=article.get('categories', []),
            tags=article.get('tags', [])
        )

        article['sentiment'] = sentiment_result

        self._save_to_file(article)

        # self.rabbit.publish(self.output_queue, article)

        write_last_timestamp(article.get('site_name', ''),
                             article.get('publication_timestamp', ''))

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _save_to_file(self, article: Dict[str, Any]) -> None:
        '''
        Save the sentiment-enriched article to a JSON file.

        Args:
            article:
                The full article object including sentiment results.

        Notes:
            - The temporary 'raw_filename' field is removed before saving.
        '''
        filename: str = article['raw_filename']
        filepath = os.path.join(self.out_dir, f'{filename}.json')

        del article['raw_filename']  # Remove raw filename before saving

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)

    def start(self) -> None:
        '''
        Start consuming cleaned news articles from the input queue.

        The worker will listen indefinitely and process messages using `handle_message`.
        '''
        print(f'[SentimentWorker] Listening on queue: {self.input_queue}')
        self.rabbit.consume(self.input_queue, callback=self.handle_message)
