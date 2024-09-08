"""Custom exceptions"""


class CommandProcessError(Exception):
    """Exceptions related to command subprocess handling"""

    def __init__(self, command: str, message: str) -> None:
        super().__init__(f"Error when sending command [{command}] ==> {message}")


class UnsupportedSystemConfiguration(Exception):
    """Could not find a suitable Wifi Driver"""

    def __init__(self, message: str) -> None:
        super().__init__(f"Error when detecting Wifi Driver: {message}")
