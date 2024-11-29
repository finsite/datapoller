import os


def validate_environment_variables(required_variables: list[str]) -> None:
    """
    Verify that all required environment variables are set.

    Args:
        required_variables (list[str]): A list of environment variables that are required for the script to run.

    Raises:
        EnvironmentError: If any of the environment variables are missing.
    """
    # Check that required_variables is a list
    if not isinstance(required_variables, list):
        raise TypeError("required_variables must be a list of strings")

    # Check that all required variables are set
    missing_variables = [
        variable for variable in required_variables if variable not in os.environ
    ]

    # Raise an error if any variables are missing
    if missing_variables:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_variables)}"
        )
