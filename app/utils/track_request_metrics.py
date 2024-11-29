import logging


def track_request_metrics(status: str, endpoint: str, response_time: float) -> None:
    """
    Tracks metrics for individual API requests.

    Args:
        status (str): The status of the request ('success' or 'failure').
        endpoint (str): The API endpoint that was accessed.
        response_time (float): The time taken for the API request in seconds.

    Raises:
        ValueError: If the status is not 'success' or 'failure'.
    """
    if status not in {"success", "failure"}:
        raise ValueError("Invalid status. Must be 'success' or 'failure'.")

    if status == "success":
        logging.info(
            "Request to %s completed successfully in %.2f seconds.",
            endpoint,
            response_time,
        )
    else:
        logging.error(
            "Request to %s failed after %.2f seconds.", endpoint, response_time
        )
