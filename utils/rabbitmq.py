import os
import json
import pika
from dotenv import load_dotenv

load_dotenv()


class RabbitMQClient:
    '''
    A reusable RabbitMQ client for publishing and consuming messages.
    '''

    def __init__(self, queue_name=None, durable=True):
        self.host = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.user = os.getenv('RABBITMQ_USER')
        self.password = os.getenv('RABBITMQ_PASS')
        self.queue_name = queue_name
        self.durable = durable

        self.connection = None
        self.channel = None

        self.connect()
        if queue_name:
            self.declare_queue(queue_name)

    def connect(self):
        '''Connect to RabbitMQ with stored env credentials.'''
        credentials = pika.PlainCredentials(self.user, self.password)
        params = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=60
        )
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

    def declare_queue(self, queue_name):
        '''Declare a queue (idempotent).'''
        self.channel.queue_declare(queue=queue_name, durable=self.durable)

    def publish(self, queue_name, message_dict):
        '''Publish a message to the specified queue.'''
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message_dict, ensure_ascii=False).encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2  # persistent
            )
        )

    def consume(self, queue_name, callback, prefetch=1):
        '''Start consuming messages from the specified queue.'''
        self.channel.queue_declare(queue=queue_name, durable=self.durable)
        self.channel.basic_qos(prefetch_count=prefetch)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=lambda ch, method, props, body:
                callback(ch, method, props, json.loads(body.decode('utf-8')))
        )
        print(f' [*] Waiting for messages in "{queue_name}" ...')
        self.channel.start_consuming()

    def close(self):
        '''Close the RabbitMQ connection.'''
        if self.connection:
            self.connection.close()
