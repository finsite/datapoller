# import pika

# from app.queue.queue_sender import QueueSender
# from app.utils.setup_logger import setup_logger
# from app.utils.validate_environment_variables import validate_environment_variables

# # Initialize logger
# logger = setup_logger()


# class BasePoller:
#     def __init__(self, queue_type: str, queue_url: str):
#         """
#         Initializes the base poller by configuring the queue dynamically by environment.
#         Validates required environment variables and initializes the appropriate queue.
#         """
#         # Validate required environment variables
#         required_env_vars = ["QUEUE_TYPE", "QUEUE_URL"]
#         validate_environment_variables(required_env_vars)

#         # Ensure the QUEUE_TYPE is either SQS or RabbitMQ
#         if queue_type not in {"sqs", "rabbitmq"}:
#             raise ValueError("QUEUE_TYPE must be either 'sqs' or 'rabbitmq'.")

#         # Initialize the QueueSender, which will handle sending to the appropriate queue
#         self.queue_sender = QueueSender(queue_type=queue_type, queue_url=queue_url)

#         # If using RabbitMQ, initialize connection and channel attributes
#         if queue_type == "rabbitmq":
#             self.connection = None
#             self.channel = None

#     def connect_to_rabbitmq(self):
#         """
#         Establishes a connection to RabbitMQ and opens a channel for message publishing.
#         """
#         if not self.connection or self.connection.is_closed:
#             try:
#                 # Establish a new connection to RabbitMQ
#                 self.connection = pika.BlockingConnection(
#                     pika.URLParameters(self.queue_sender.queue_url)
#                 )
#                 self.channel = self.connection.channel()
#                 logger.info("Connected to RabbitMQ successfully.")
#             except Exception as e:
#                 logger.error(f"Failed to connect to RabbitMQ: {e}")
#                 raise

#     def send_to_queue(self, payload: dict):
#         """
#         Sends the processed payload to the configured queue (SQS or RabbitMQ).

#         Args:
#             payload (dict): The data to send to the queue.
#         """
#         try:
#             if self.queue_sender.queue_type == "rabbitmq":
#                 # If using RabbitMQ, ensure the connection is established
#                 self.connect_to_rabbitmq()

#                 # Publish message to RabbitMQ
#                 self.channel.basic_publish(
#                     exchange="",  # Default exchange
#                     routing_key=self.queue_sender.queue_url.split("/")[
#                         -1
#                     ],  # Queue name
#                     body=str(payload),
#                     properties=pika.BasicProperties(
#                         delivery_mode=2,  # Make the message persistent
#                     ),
#                 )
#                 logger.info("Successfully sent message to RabbitMQ queue.")
#             else:
#                 # If using SQS, delegate to the QueueSender
#                 self.queue_sender.send_message(payload)
#                 logger.info("Successfully sent message to SQS queue.")
#         except Exception as e:
#             logger.error(
#                 f"Failed to send message to the {self.queue_sender.queue_type} queue: {e}"
#             )
#             raise

#     def close_connection(self):
#         """
#         Closes the RabbitMQ connection if it exists.
#         """
#         if self.queue_sender.queue_type == "rabbitmq" and self.connection:
#             try:
#                 self.connection.close()
#                 logger.info("Closed RabbitMQ connection.")
#             except Exception as e:
#                 logger.error(f"Failed to close RabbitMQ connection: {e}")
#                 raise
import pika
from app.queue.queue_sender import QueueSender
from app.utils.setup_logger import setup_logger
from app.utils.validate_environment_variables import validate_environment_variables

# Initialize logger
logger = setup_logger(__name__)


class BasePoller:
    """
    Base class for pollers that handles dynamic queue configuration and message sending.
    """

    def __init__(self, queue_type: str, queue_url: str):
        """
        Initializes the BasePoller with dynamic queue configuration.

        Args:
            queue_type (str): The type of the queue ('sqs' or 'rabbitmq').
            queue_url (str): The URL of the queue.

        Raises:
            ValueError: If the queue type is invalid.
        """
        # Validate required environment variables
        validate_environment_variables(["QUEUE_TYPE", "QUEUE_URL"])

        # Ensure valid queue type
        if queue_type not in {"sqs", "rabbitmq"}:
            logger.error("QUEUE_TYPE must be either 'sqs' or 'rabbitmq'.")
            raise ValueError("QUEUE_TYPE must be either 'sqs' or 'rabbitmq'.")

        # Initialize the QueueSender
        self.queue_sender = QueueSender(queue_type=queue_type, queue_url=queue_url)

        # RabbitMQ-specific attributes
        self.connection = None
        self.channel = None

    def connect_to_rabbitmq(self) -> None:
        """
        Establishes a connection to RabbitMQ and opens a channel for message publishing.
        """
        try:
            if not self.connection or self.connection.is_closed:
                self.connection = pika.BlockingConnection(
                    pika.URLParameters(self.queue_sender.queue_url)
                )
                self.channel = self.connection.channel()
                logger.info("Connected to RabbitMQ successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def send_to_queue(self, payload: dict) -> None:
        """
        Sends the processed payload to the configured queue (SQS or RabbitMQ).

        Args:
            payload (dict): The data to send to the queue.

        Raises:
            Exception: If sending the message fails.
        """
        try:
            if self.queue_sender.queue_type == "rabbitmq":
                self._send_to_rabbitmq(payload)
            else:
                self._send_to_sqs(payload)
        except Exception as e:
            logger.error(
                f"Failed to send message to the {self.queue_sender.queue_type} queue: {e}"
            )
            raise

    def _send_to_rabbitmq(self, payload: dict) -> None:
        """
        Publishes the message to a RabbitMQ queue.

        Args:
            payload (dict): The data to publish.
        """
        try:
            self.connect_to_rabbitmq()
            queue_name = self.queue_sender.queue_url.split("/")[-1]  # Extract queue name
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=str(payload),
                properties=pika.BasicProperties(delivery_mode=2),  # Persistent messages
            )
            logger.info(f"Message successfully sent to RabbitMQ queue: {queue_name}.")
        except Exception as e:
            logger.error(f"Error while sending message to RabbitMQ: {e}")
            raise

    def _send_to_sqs(self, payload: dict) -> None:
        """
        Delegates sending the message to the SQS queue using QueueSender.

        Args:
            payload (dict): The data to send to SQS.
        """
        try:
            self.queue_sender.send_message(payload)
            logger.info("Message successfully sent to SQS queue.")
        except Exception as e:
            logger.error(f"Error while sending message to SQS: {e}")
            raise

    def close_connection(self) -> None:
        """
        Closes the RabbitMQ connection if it exists.
        """
        if self.queue_sender.queue_type == "rabbitmq" and self.connection:
            try:
                self.connection.close()
                logger.info("RabbitMQ connection closed.")
            except Exception as e:
                logger.error(f"Failed to close RabbitMQ connection: {e}")
                raise
