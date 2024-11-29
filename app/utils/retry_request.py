import time
import typing


def retry_request(
    func: typing.Callable[[], typing.Any],
    *,
    max_retries: int = 3,
    delay_seconds: int = 5
) -> typing.Any:
    """
    Retries a given function if it raises an exception.

    Args:
        func: The function to be retried.
        max_retries: The maximum number of retry attempts. Defaults to 3.
        delay_seconds: The delay in seconds between retries. Defaults to 5.

    Returns:
        The result of the function if successful.

    Raises:
        ValueError: If the function to be retried is None.
        Exception: The last exception encountered if all retries fail.
    """
    if func is None:
        raise ValueError("The function to be retried cannot be None")

    for attempt in range(max_retries):
        try:
            return func()
        except Exception as exception:
            if attempt < max_retries - 1:
                time.sleep(delay_seconds)
            else:
                raise exception from None
