import logging


def track_polling_metrics(status: str, source: str, symbol: str) -> None:
    """
    Tracks metrics for polling operations.

    Args:
        status (str): The status of the operation ('success' or 'failure').
        source (str): The source of the polling data (e.g., 'yfinance', 'finnhub').
        symbol (str): The symbol for which polling was performed.

    Raises:
        ValueError: If the status is not 'success' or 'failure'.
    """
    if status not in {"success", "failure"}:
        raise ValueError("Invalid status. Must be 'success' or 'failure'.")

    if status == "success":
        logging.info("Polling successful for %s from %s.", symbol, source)
    else:
        logging.error("Polling failed for %s from %s.", symbol, source)
