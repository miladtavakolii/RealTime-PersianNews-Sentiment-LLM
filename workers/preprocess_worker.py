import os
import json
from utils.rabbitmq import RabbitMQClient
from preprocessing.clean_text import TextCleaner


class PreprocessWorker:

    def __init__(self, input_queue="raw_news", output_queue="clean_news", out_dir="data/cleaned"):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.out_dir = out_dir

        # Ensure output directory exists
        os.makedirs(self.out_dir, exist_ok=True)

        # Singleton RabbitMQ client
        self.rabbit = RabbitMQClient()

        # Declare queues (idempotent)
        self.rabbit.declare_queue(self.input_queue)
        self.rabbit.declare_queue(self.output_queue)

        # Text cleaner instance
        self.text_cleaner = TextCleaner()

    def handle_message(self, ch, method, props, article):
        '''Process a single message from the input queue.'''
        # Clean text fields
        article["title"] = self.text_cleaner.clean(article["title"])
        article["content"] = self.text_cleaner.clean(article["content"])
        article["summary"] = self.text_cleaner.clean(article["summary"])

        # Save cleaned file locally
        self._save_to_file(article)

        # Send cleaned message to next queue
        self.rabbit.publish(self.output_queue, article)

        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _save_to_file(self, article):
        '''Save cleaned article to a JSON file in the output directory.'''
        filename = article["raw_filename"]
        filepath = os.path.join(self.out_dir, f"{filename}.json")
        del article["raw_filename"]  # Remove raw filename before saving

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(article, f, ensure_ascii=False, indent=2)

    def start(self):
        '''Start consuming messages from the input queue.'''
        print(f"[PreprocessWorker] Listening on queue: {self.input_queue}")
        self.rabbit.consume(self.input_queue, callback=self.handle_message)
