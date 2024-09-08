"""Common logging setup"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from rich import traceback
from rich.logging import RichHandler


class Logger:
    """A singleton class to manage logging for the internal modules

    Args:
        logger (logging.Logger): input logger that will be modified and then returned
        output (Path | None): Path of log file for file stream handler. If not set, will not log to file.
        modules (list[str] | None): Optional override of modules / levels. Will be merged into default modules.
    """

    _instances: dict[type[Logger], Logger] = {}

    def __new__(cls, *_: Any) -> Any:  # noqa https://github.com/PyCQA/pydocstyle/issues/515
        if cls not in cls._instances:
            c = object.__new__(cls)
            cls._instances[cls] = c
            return c
        raise RuntimeError("The logger can only be setup once and this should be done at the top level.")

    def __init__(
        self,
        logger: logging.Logger,
        output: Path | None = None,
        modules: list[str] | None = None,
    ) -> None:
        # TODO automatically discover somehow?
        self.modules = [
            "pywificli.util",
        ]

        self.logger = logger
        self.modules = modules or self.modules
        self.handlers: list[logging.Handler] = []

        self.file_handler: logging.Handler | None
        if output:
            # Logging to file with millisecond timing
            self.file_handler = logging.FileHandler(output, mode="w")
            file_formatter = logging.Formatter(
                fmt="%(threadName)13s:%(asctime)s.%(msecs)03d %(filename)-40s %(lineno)4s %(levelname)-8s | %(message)s",
                datefmt="%H:%M:%S",
            )
            self.file_handler.setFormatter(file_formatter)
            # Set to TRACE for concurrency debugging
            self.file_handler.setLevel(logging.DEBUG)
            logger.addHandler(self.file_handler)
            self.addLoggingHandler(self.file_handler)
        else:
            self.file_handler = None

        # Use Rich for colorful console logging
        self.stream_handler = RichHandler(rich_tracebacks=True, enable_link_path=True, show_time=False)
        stream_formatter = logging.Formatter("%(asctime)s.%(msecs)03d %(message)s", datefmt="%H:%M:%S")
        self.stream_handler.setFormatter(stream_formatter)
        self.stream_handler.setLevel(logging.INFO)
        logger.addHandler(self.stream_handler)
        self.addLoggingHandler(self.stream_handler)

        traceback.install()  # Enable exception tracebacks in rich logger

    @classmethod
    def get_instance(cls) -> Logger:
        """Get the singleton instance

        Raises:
            RuntimeError: Has not yet been instantiated

        Returns:
            Logger: singleton instance
        """
        if not (logger := cls._instances.get(Logger, None)):
            raise RuntimeError("Logging must first be setup")
        return logger

    def addLoggingHandler(self, handler: logging.Handler) -> None:
        """Add a handler for all of the internal modules

        Args:
            handler (logging.Handler): handler to add
        """
        self.logger.addHandler(handler)
        self.handlers.append(handler)

        # Enable / disable logging in modules
        for module in self.modules:
            l = logging.getLogger(module)
            l.addHandler(handler)


def setup_logging(
    base: logging.Logger | str,
    output: Path | None = None,
    modules: list[str] | None = None,
) -> logging.Logger:
    """Configure the modules for logging and get a logger that can be used by the application

    This can only be called once and should be done at the top level of the application.

    Args:
        base (logging.Logger | str): Name of application (i.e. __name__) or preconfigured logger to use as base
        output (Path | None): Path of log file for file stream handler. If not set, will not log to file.
        modules (list[str] | None): Optional override of modules / levels. Will be merged into default modules.

    Raises:
        TypeError: Base logger is not of correct type

    Returns:
        logging.Logger: updated logger that the application can use for logging
    """
    if isinstance(base, str):
        base = logging.getLogger(base)
    elif not isinstance(base, logging.Logger):
        raise TypeError("Base must be of type logging.Logger or str")
    l = Logger(base, output, modules)
    return l.logger


def set_file_logging_level(level: int) -> None:
    """Change the global logging level for the default file output handler

    Args:
        level (int): level to set
    """
    if fh := Logger.get_instance().file_handler:
        fh.setLevel(level)


def set_stream_logging_level(level: int) -> None:
    """Change the global logging level for the default stream output handler

    Args:
        level (int): level to set
    """
    Logger.get_instance().stream_handler.setLevel(level)


def set_logging_level(level: int) -> None:
    """Change the global logging level for the default file and stream output handlers

    Args:
        level (int): level to set
    """
    set_file_logging_level(level)
    set_stream_logging_level(level)


def add_logging_handler(handler: logging.Handler) -> None:
    """Add a handler to all of the internal modules

    Args:
        handler (logging.Handler): handler to add
    """
    Logger.get_instance().addLoggingHandler(handler)
