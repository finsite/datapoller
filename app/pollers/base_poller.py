import abc
import logging
from app.queue_sender.queue_sender import send_to_queue

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BasePoller(abc.ABC):
    """
    Base class for all stock data pollers.
    This class defines the common interface and shared logic for all pollers.
    """
    def __init__(self, api_key):
        self.api_key = api_key

    @abc.abstractmethod
    def poll(self, symbols):
        pass

    def send_to_queue(self, data, queue_type="sqs"):
        """
        Send the polled data to the queue (SQS or RabbitMQ).
        """
        try:
            if queue_type == "sqs":
                send_to_queue(data, queue_type)
            elif queue_type == "rabbitmq":
                send_to_queue(data, queue_type)
            else:
                raise ValueError(f"Unsupported queue type: {queue_type}")
        except Exception as e:
            logger.error(f"Error sending data to {queue_type} queue: {e}")
            raise

    def log_error(self, error_message):
        """Helper method to log errors."""
        logger.error(error_message)
