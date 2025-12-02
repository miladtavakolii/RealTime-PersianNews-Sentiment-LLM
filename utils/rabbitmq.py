import os
import pika
from dotenv import load_dotenv

# Load .env file once when module is imported
load_dotenv()

def get_rabbitmq_connection():
    '''Establish and return a RabbitMQ channel using environment variables for configuration.'''
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", 5672))
    user = os.getenv("RABBITMQ_USER")
    password = os.getenv("RABBITMQ_PASS")

    credentials = pika.PlainCredentials(user, password)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials
        )
    )

    return connection.channel()
