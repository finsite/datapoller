import os
import pika
from app.queue.queue_sender import QueueSender
from app.utils.setup_logger import setup_logger
from app.utils.validate_environment_variables import validate_environment_variables

# Initialize logger
logger = setup_logger()


class BasePoller:
    def __init__(self):
        """
        Initializes the base poller by configuring the queue dynamically based on environment.
        Validates required environment variables and initializes the appropriate queue sender.
        """
        # Validate required environment variables
        required_env_vars = ["QUEUE_TYPE", "QUEUE_URL"]
        validate_environment_variables(required_env_vars)

        # Fetch queue configuration from environment variables
        self.queue_type = os.getenv("QUEUE_TYPE").lower()
        self.queue_url = os.getenv("QUEUE_URL")

        # Ensure the QUEUE_TYPE is either SQS or RabbitMQ
        if self.queue_type not in {"sqs", "rabbitmq"}:
            raise ValueError("QUEUE_TYPE must be either 'sqs' or 'rabbitmq'.")

        # Initialize the QueueSender, which will handle sending to the appropriate queue type
        self.queue_sender = QueueSender(
            queue_type=self.queue_type, queue_url=self.queue_url
        )

        # If using RabbitMQ, initialize connection and channel attributes
        if self.queue_type == "rabbitmq":
            self.connection = None
            self.channel = None

    def connect_to_rabbitmq(self):
        """
        Establishes a connection to RabbitMQ and opens a channel for message publishing.
        """
        if not self.connection or self.connection.is_closed:
            try:
                # Establish a new connection to RabbitMQ
                self.connection = pika.BlockingConnection(
                    pika.URLParameters(self.queue_url)
                )
                self.channel = self.connection.channel()
                logger.info("Connected to RabbitMQ successfully.")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise

    def send_to_queue(self, payload: dict):
        """
        Sends the processed payload to the configured queue (SQS or RabbitMQ).

        Args:
            payload (dict): The data to send to the queue.
        """
        try:
            if self.queue_type == "rabbitmq":
                # If using RabbitMQ, ensure the connection is established
                self.connect_to_rabbitmq()

                # Publish message to RabbitMQ
                self.channel.basic_publish(
                    exchange="",  # Default exchange
                    routing_key=self.queue_url.split("/")[-1],  # Queue name
                    body=str(payload),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Make the message persistent
                    ),
                )
                logger.info("Successfully sent message to RabbitMQ queue.")
            else:
                # If using SQS, delegate to the QueueSender
                self.queue_sender.send_message(payload)
                logger.info("Successfully sent message to SQS queue.")
        except Exception as e:
            logger.error(f"Failed to send message to the {self.queue_type} queue: {e}")
            raise

    def close_connection(self):
        """
        Closes the RabbitMQ connection if it exists.
        """
        if self.queue_type == "rabbitmq" and self.connection:
            try:
                self.connection.close()
                logger.info("Closed RabbitMQ connection.")
            except Exception as e:
                logger.error(f"Failed to close RabbitMQ connection: {e}")
                raise
