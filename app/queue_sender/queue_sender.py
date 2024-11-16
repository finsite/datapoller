import boto3
import pika
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_to_queue(data, queue_type="sqs"):
    try:
        if queue_type == "sqs":
            send_to_sqs(data)
        elif queue_type == "rabbitmq":
            send_to_rabbitmq(data)
        else:
            raise ValueError(f"Unsupported queue type: {queue_type}")
    except Exception as e:
        logger.error(f"Error in send_to_queue: {e}")
        raise

def send_to_sqs(data):
    try:
        sqs = boto3.client("sqs")
        queue_url = os.getenv("SQS_QUEUE_URL")
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=str(data)
        )
    except Exception as e:
        logger.error(f"Error sending to SQS: {e}")
        raise

def send_to_rabbitmq(data):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST")))
        channel = connection.channel()
        channel.queue_declare(queue=os.getenv("RABBITMQ_QUEUE"))
        channel.basic_publish(
            exchange='',
            routing_key=os.getenv("RABBITMQ_QUEUE"),
            body=str(data)
        )
        connection.close()
    except Exception as e:
        logger.error(f"Error sending to RabbitMQ: {e}")
        raise
