import logging
from enum import Enum, unique
from typing import Optional, Union

import colorlog

###################################################################################################
# LogLevel Enum
###################################################################################################
_NOTSET_DESC = (
    "When set on a logger, indicates that ancestor loggers are to be consulted to determine the "
    "effective level. If that still resolves to NOTSET, then all events are logged. "
    "When set on a handler, all events are handled."
)
_DEBUG_DESC = (
    "Detailed information, typically only of interest to a developer trying to "
    "diagnose a problem."
)
_INFO_DESC = "Confirmation that things are working as expected."
_WARNING_DESC = (
    "An indication that something unexpected happened, "
    "or that a problem might occur in the near future (e.g. 'disk space low'). "
    "The software is still working as expected."
)
_ERROR_DESC = "Due to a more serious problem, the software has not been able to perform some function."
_CRITICAL_DESC = "A serious error, indicating that the program itself may be unable to continue running."


@unique
class LogLevel(Enum):
    """
    Enumeration of log levels with associated integer values and descriptions.

    Each log level has a unique integer value and a description of its purpose.
    """

    NOTSET = (0, _NOTSET_DESC)
    DEBUG = (10, _DEBUG_DESC)
    INFO = (20, _INFO_DESC)
    WARNING = (30, _WARNING_DESC)
    ERROR = (40, _ERROR_DESC)
    CRITICAL = (50, _CRITICAL_DESC)

    def __new__(cls, value: int, description: str) -> "LogLevel":
        """
        Create a new LogLevel instance.

        Args:
            value (int): The integer value associated with the log level.
            description (str): A description of the log level's purpose.

        Returns:
            LogLevel: A new LogLevel instance.
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @property
    def value(self) -> int:
        """
        Get the integer value of the log level.

        Returns:
            int: The integer value of the log level.
        """
        return self._value_

    @property
    def formatted(self) -> str:
        """
        Get a formatted string representation of the log level.

        Returns:
            str: A string in the format "NAME (VALUE)".
        """
        return f"{self.name} ({self.value})"

    @classmethod
    def get(cls, value: int):
        """
        Get a LogLevel instance from its integer value.

        Args:
            value (int): The integer value of the log level.

        Returns:
            LogLevel: The corresponding LogLevel instance.

        Raises:
            ValueError: If no LogLevel matches the given value.
        """
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"No LogLevel with value {value}")


# Aliases
LogLevel.WARN = LogLevel.WARNING
LogLevel.FATAL = LogLevel.CRITICAL


###################################################################################################
# Toad Logger
###################################################################################################
class ToadLogger:
    """
    A custom logger class that wraps the standard Python logging module.

    This logger supports colored output and provides a simplified interface for logging.
    """

    DEFAULT_LOG_LEVEL = LogLevel.INFO

    def __init__(
        self,
        name: str,
        level: Optional[Union[int, LogLevel]] = DEFAULT_LOG_LEVEL,
        color: Optional[bool] = True,
    ):
        """
        Initialize a ToadLogger instance.

        Args:
            name (str): The name of the logger.
            level (Optional[Union[int, LogLevel]], optional): The log level. Defaults to INFO.
            color (Optional[bool], optional): Whether to use colored output. Defaults to True.
        """
        self.name = name
        self.color = color
        self.level = self._validate_level(level)
        self.logger = self._setup()

    def __getattr__(self, name):
        """
        Delegate attribute access to the underlying logger.

        Args:
            name (str): The name of the attribute.

        Returns:
            Any: The value of the attribute from the underlying logger.
        """
        return getattr(self.logger, name)

    def _setup(self):
        """
        Set up the logger with appropriate handlers and formatters.

        Returns:
            Union[colorlog.ColoredLogger, logging.Logger]: The configured logger instance.
        """
        logger = (
            colorlog.getLogger(self.name)
            if self.color
            else logging.getLogger(self.name)
        )
        logger.setLevel(self.level)
        handler = colorlog.StreamHandler() if self.color else logging.StreamHandler()
        handler.setFormatter(self._get_formatter())
        logger.addHandler(handler)
        return logger

    def _get_formatter(self):
        """
        Get the appropriate formatter based on whether color is enabled.

        Returns:
            Union[colorlog.ColoredFormatter, logging.Formatter]: The configured formatter.
        """
        if self.color:
            return colorlog.ColoredFormatter(**self.formatter_params)
        return logging.Formatter(**self.formatter_params)

    @property
    def formatter_params(self):
        """
        Get the parameters for the log formatter.

        Returns:
            dict: A dictionary of formatter parameters.
        """
        params = {
            "fmt": "%(levelname)s - %(asctime)s  |  %(name)s:  %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
        if self.color:
            params["fmt"] = "%(log_color)s" + params.get("fmt")
            params["log_colors"] = {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            }
        print(f"Formatter Params: {params}")
        return params

    def _validate_level(self, level: Optional[Union[int, LogLevel]]) -> int:
        """
        Validate and convert the input log level to an integer value.

        Args:
            level (Optional[Union[int, LogLevel]]): The input log level.

        Returns:
            int: The validated log level as an integer.
        """
        setting_default_msg = (
            f"Setting to default level: {self.DEFAULT_LOG_LEVEL.formatted}"
        )
        if level is None:
            print(f"Logging level not provided... {setting_default_msg}")
            return self.DEFAULT_LOG_LEVEL.value

        if isinstance(level, LogLevel):
            return level.value

        if isinstance(level, int):
            try:
                return LogLevel.get(level).value
            except ValueError:
                print(f"Invalid logging level: {level}... {setting_default_msg}")
                return self.DEFAULT_LOG_LEVEL.value

        print(f"I'm sorry Dave, I'm afraid I can't do that... {setting_default_msg}")
        return self.DEFAULT_LOG_LEVEL.value


if __name__ == "__main__":
    # Test LogLevel Enum
    print(f"\n{LogLevel.INFO.value}")  # 20
    print(
        LogLevel.INFO.description
    )  # "Confirmation that things are working as expected."
    print(LogLevel.get(40))  # LogLevel.ERROR
    print(LogLevel.DEBUG.formatted)  # DEBUG (10)
    print(f"{LogLevel.WARN == LogLevel.WARNING}\n")  # True

    # Test Toad Logger
    logger = ToadLogger("toad_logger", LogLevel.DEBUG)
    logger.debug("This is a test debug message.")
    logger.info("This is a test info message.")
    logger.warning("This is a test warning message.")
    logger.error("This is a test error message.")
    logger.critical("This is a test critical message.")
