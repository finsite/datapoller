from app.queue_sender.queue_sender import QueueSender
from pollers.yfinance_poller import YFinancePoller
from pollers.polygon_poller import PolygonPoller
from pollers.iex_poller import IexPoller
from pollers.alphavantage_poller import AlphaVantagePoller
from pollers.quandl_poller import QuandlPoller
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_poller():
    """
    Factory function to create a poller based on the environment variable `POLLING_PROVIDER`.
    """
    poller_type = os.getenv("POLLING_PROVIDER", "yfinance").lower()

    if poller_type == "yfinance":
        return YFinancePoller()
    elif poller_type == "polygon":
        api_key = os.getenv("POLYGON_API_KEY")
        return PolygonPoller(api_key)
    elif poller_type == "iex":
        api_key = os.getenv("IEX_API_KEY")
        return IexPoller(api_key)
    elif poller_type == "alphavantage":
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        return AlphaVantagePoller(api_key)
    elif poller_type == "quandl":
        api_key = os.getenv("QUANDL_API_KEY")
        return QuandlPoller(api_key)
    else:
        logger.error(f"Unsupported polling provider: {poller_type}")
        raise ValueError(f"Unsupported polling provider: {poller_type}")

def main():
    # Create poller and queue sender
    poller = create_poller()  # Use the factory to get the correct poller
    queue_sender = QueueSender()

    symbols = ["AAPL", "GOOGL", "AMZN"]
    
    try:
        # Polling data from the selected provider
        data = poller.poll(symbols)
        logger.info(f"Polled data: {data}")
        
        # Send the polled data to the selected queue (SQS or RabbitMQ)
        queue_sender.send_to_queue(data)
        logger.info("Data sent to queue successfully.")
        
    except Exception as e:
        logger.error(f"Error occurred during polling or sending data: {e}")
    finally:
        # Ensure the queue connection is properly closed, if necessary
        queue_sender.close()

if __name__ == "__main__":
    main()




# import boto3
# from botocore.exceptions import ClientError
# import json
# import logging
# import os
# import pika
# import requests
# import time

# # Set up logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Environment variables
# QUEUE_TYPE = os.environ.get('QUEUE_TYPE', 'sqs')  
# STOCK_API = os.environ.get('STOCK_API', 'alphavantage')  

# # Initialize clients based on queue type
# if QUEUE_TYPE == 'sqs':
#     sqs = boto3.client('sqs')
# elif QUEUE_TYPE == 'rabbitmq':
#     rabbitmq_url = os.environ.get('RABBITMQ_URL')
#     rabbitmq_queue = os.environ.get('RABBITMQ_QUEUE')
# else:
#     logging.error(f"Invalid QUEUE_TYPE: {QUEUE_TYPE}. Must be 'sqs', 'rabbitmq'.")
#     raise ValueError(f"Invalid QUEUE_TYPE: {QUEUE_TYPE}")

# def fetch_stock_data():
#     try:
#         if STOCK_API == 'alphavantage':
#             api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
#             symbol = 'AAPL'  # Example symbol, replace with dynamic input if needed
#             api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}'
#             response = requests.get(api_url)
#             response.raise_for_status()
#             data = response.json()
#             return [{'symbol': symbol, 'price': float(data['Time Series (1min)'][next(iter(data['Time Series (1min)']))]['1. open'])}]
        
#         elif STOCK_API == 'iexcloud':
#             api_key = os.environ.get('IEXCLOUD_API_KEY')
#             symbol = 'AAPL'  # Example symbol, replace with dynamic input if needed
#             api_url = f'https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={api_key}'
#             response = requests.get(api_url)
#             response.raise_for_status()
#             data = response.json()
#             return [{'symbol': symbol, 'price': data['latestPrice']}]

#         elif STOCK_API == 'finnhub':
#             api_key = os.environ.get('FINNHUB_API_KEY')
#             symbol = 'AAPL'  # Example symbol, replace with dynamic input if needed
#             api_url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}'
#             response = requests.get(api_url)
#             response.raise_for_status()
#             data = response.json()
#             return [{'symbol': symbol, 'price': data['c']}]  # Current price

#         else:
#             logging.error(f"Invalid STOCK_API: {STOCK_API}. Must be 'alphavantage', 'iexcloud', or 'finnhub'.")
#             raise ValueError(f"Invalid STOCK_API: {STOCK_API}")

#     except requests.RequestException as e:
#         logging.error(f"Error fetching stock data: {e}")
#         return []

# def main():
#     while True:
#         stock_data = fetch_stock_data()

#         for stock in stock_data:
#             stock_symbol = stock.get('symbol')
#             price = stock.get('price')

#             if stock_symbol is None or price is None:
#                 logging.warning("Stock data missing required fields.")
#                 continue
            
#             # Prepare message
#             message = json.dumps(stock)
#             logging.info(f"Processing stock: {stock_symbol}, Price: {price}")

#             # Send message to the appropriate queue
#             try:
#                 if QUEUE_TYPE == 'sqs':
#                     queue_url = determine_sqs_queue(price)
#                     sqs.send_message(
#                         QueueUrl=queue_url,
#                         MessageBody=message
#                     )
#                     logging.info(f"Sent message to SQS queue: {queue_url}")
#                 elif QUEUE_TYPE == 'rabbitmq':
#                     send_to_rabbitmq(message)
#             except Exception as e:
#                 logging.error(f"Error sending message: {e}")

#         time.sleep(60)  # Poll every 60 seconds


# def send_to_rabbitmq(message):
#     try:
#         connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
#         channel = connection.channel()
#         channel.queue_declare(queue=rabbitmq_queue, durable=True)
#         channel.basic_publish(
#             exchange='',
#             routing_key=rabbitmq_queue,
#             body=message,
#             properties=pika.BasicProperties(
#                 delivery_mode=2,  # Make message persistent
#             )
#         )
#         connection.close()
#         logging.info(f"Sent message to RabbitMQ queue: {rabbitmq_queue}")
#     except Exception as e:
#         logging.error(f"Error sending to RabbitMQ: {e}")

# if __name__ == "__main__":
#     main()