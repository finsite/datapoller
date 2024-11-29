import logging


# Initialize the logger
logger = logging.getLogger(__name__)


def validate_data(data):
    """
    Validates the data to ensure it conforms to the required schema.

    Parameters:
        data (dict): The data to validate.

    Returns:
        bool: True if data is valid, False otherwise.
    """
    required_keys = {"symbol", "price", "volume", "timestamp"}

    try:
        if not isinstance(data, dict):
            logger.error("Invalid data type. Expected a dictionary.")
            return False

        # Check if all required keys are present
        missing_keys = required_keys - data.keys()
        if missing_keys:
            logger.error(f"Missing required keys in data: {missing_keys}")
            return False

        # Validate each field
        if not isinstance(data["symbol"], str) or not data["symbol"].isalpha():
            logger.error(f"Invalid symbol format: {data['symbol']}")
            return False

        if not isinstance(data["price"], (int, float)) or data["price"] < 0:
            logger.error(f"Invalid price: {data['price']}")
            return False

        if not isinstance(data["volume"], int) or data["volume"] < 0:
            logger.error(f"Invalid volume: {data['volume']}")
            return False

        if not isinstance(data["timestamp"], str):
            logger.error(f"Invalid timestamp format: {data['timestamp']}")
            return False

        return True

    except Exception as e:
        logger.error(f"An error occurred during data validation: {e}")
        return False
