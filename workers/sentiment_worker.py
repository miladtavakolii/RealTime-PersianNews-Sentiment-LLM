import os
import json
from typing import Any, Dict

from utils.rabbitmq import RabbitMQClient
from sentiment_engine.engine import SentimentEngine
from sentiment_engine.ollama_client import OllamaClient


class SentimentWorker:
    '''
    Worker responsible for:
    - Receiving cleaned news from RabbitMQ
    - Performing sentiment analysis using an injected LLM engine
    - Saving results locally
    - Publishing result to the next queue
    '''

    def __init__(self, model_info: dict, input_queue: str = 'clean_news', output_queue: str = 'sentiment_news', out_dir: str = 'data/sentiments'):
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
        provider = OllamaClient(
            model=model_info['name'], prompt_template=prompt_template)

        self.engine = SentimentEngine(provider=provider)

    def handle_message(self, ch: Any, method: Any, props: Any, article: Dict[str, Any]) -> None:
        '''
        Process a cleaned news article:
        - Run LLM for sentiment
        - Save JSON
        - Publish to next queue
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

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _save_to_file(self, article: Dict[str, Any]) -> None:
        '''
        Save sentiment-enriched article as .json
        '''
        filename = article.get('clean_filename', 'unknown')
        filepath = os.path.join(self.out_dir, f'{filename}.json')

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)

    def start(self) -> None:
        print(f'[SentimentWorker] Listening on queue: {self.input_queue}')
        self.rabbit.consume(self.input_queue, callback=self.handle_message)
