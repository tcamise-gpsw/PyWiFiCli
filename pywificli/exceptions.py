"""Custom exceptions"""


class CommandProcessError(Exception):
    """Exceptions related to command subprocess handling"""

    def __init__(self, command: str, message: str) -> None:
        super().__init__(f"Error when sending command [{command}] ==> {message}")
