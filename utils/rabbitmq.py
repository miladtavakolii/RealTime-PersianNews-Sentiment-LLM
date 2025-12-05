import os
import json
import pika
from dotenv import load_dotenv
from typing import Optional, Any

import pika.channel

load_dotenv()


class RabbitMQClient:
    '''
    A reusable RabbitMQ client for message publishing and consumption.

    This class provides a thin abstraction around RabbitMQ operations,
    offering:
        - Automatic connection management via environment variables
        - Queue declaration (idempotent)
        - JSON-based message publishing
        - Message consumption with a callback function
        - Optional persistent/durable queue configuration

    Attributes:
        host: RabbitMQ server hostname.
        port: RabbitMQ server port.
        user: Username for authentication.
        password: Password for authentication.
        queue_name: Default queue name for publish/consume.
        durable: Whether declared queues survive server restarts.
        connection: Active RabbitMQ connection.
        channel: Active RabbitMQ communication channel.
    '''

    def __init__(self, queue_name: Optional[str] = None, durable: bool = True):
        '''
        Initialize the RabbitMQ client using environment variable configuration.

        Optionally declares an initial queue if `queue_name` is provided.

        Args:
            queue_name: Name of the default queue to declare and use.
            durable: If True, queues are created as durable and persist across restarts.
        '''
        self.host: str = os.getenv('RABBITMQ_HOST', 'localhost')
        self.port: int = int(os.getenv('RABBITMQ_PORT', 5672))
        self.user: Optional[str] = os.getenv('RABBITMQ_USER')
        self.password: Optional[str] = os.getenv('RABBITMQ_PASS')
        self.queue_name: Optional[str] = queue_name
        self.durable: bool = durable

        self.connection: pika.adapters.BaseConnection = None
        self.channel: pika.channel.Channel = None

        self.connect()
        if queue_name:
            self.declare_queue(queue_name)

    def connect(self) -> None:
        '''
        Establish a connection to the RabbitMQ server using credentials loaded from environment.

        Raises:
            pika.exceptions.AMQPConnectionError:
                If the client fails to connect to the server.
        '''
        credentials = pika.PlainCredentials(self.user, self.password)
        params = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=60
        )
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

    def declare_queue(self, queue_name: str) -> None:
        '''
        Declare a queue if it does not already exist.

        This operation is idempotent: calling it multiple times has no side effects.

        Args:
            queue_name: Name of the queue to declare.
        '''
        self.channel.queue_declare(queue=queue_name, durable=self.durable)

    def publish(self, queue_name: str, message_dict: dict) -> None:
        '''
        Publish a JSON-serializable message to the specified queue.

        Args:
            queue_name: Queue to publish the message into.
            message_dict: Dictionary that will be serialized as JSON and placed in the queue.

        Notes:
            - Messages are published as UTF-8 encoded JSON.
            - delivery_mode=2 ensures message persistence.
        '''
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message_dict, ensure_ascii=False).encode('utf-8'),
            properties=pika.BasicProperties(
                delivery_mode=2  # persistent
            )
        )

    def consume(self, queue_name: str, callback: Any, prefetch: int = 1) -> None:
        '''
        Start consuming messages from a queue and process each message using a callback.

        Args:
            queue_name: Queue to consume messages from.
            callback: Function with signature: callback(ch, method, props, message_dict)
            prefetch: Maximum number of unacknowledged messages the worker can receive.

        Notes:
            - Automatically JSON-decodes the message body.
            - The callback must manually acknowledge messages via `basic_ack`.
        '''    
        self.channel.queue_declare(queue=queue_name, durable=self.durable)
        self.channel.basic_qos(prefetch_count=prefetch)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=lambda ch, method, props, body:
                callback(ch, method, props, json.loads(body.decode('utf-8')))
        )
        print(f' [*] Waiting for messages in "{queue_name}" ...')
        self.channel.start_consuming()

    def close(self) -> None:
        '''
        Close the active RabbitMQ connection gracefully.
        '''
        if self.connection:
            self.connection.close()
