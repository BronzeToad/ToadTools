import logging
from enum import Enum, unique
from typing import Optional, Union, Any, Dict

import colorlog

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
    """Enumeration of logging levels with associated integer values and descriptions."""

    NOTSET = (0, _NOTSET_DESC)
    """Level NOTSET: 0 - No specific logging level set."""
    DEBUG = (10, _DEBUG_DESC)
    """Level DEBUG: 10 - Detailed information for diagnosing problems."""
    INFO = (20, _INFO_DESC)
    """Level INFO: 20 - Confirmation that things are working as expected."""
    WARNING = (30, _WARNING_DESC)
    """Level WARNING: 30 - An indication of potential issues or unexpected events."""
    ERROR = (40, _ERROR_DESC)
    """Level ERROR: 40 - Serious problems preventing some functionality."""
    CRITICAL = (50, _CRITICAL_DESC)
    """Level CRITICAL: 50 - Severe errors indicating program may not continue."""

    def __new__(cls, value: int, description: str) -> "LogLevel":
        """Creates a new instance of LogLevel.

        Args:
            value (int): The integer value of the log level.
            description (str): A description of the log level.

        Returns:
            LogLevel: A new instance of LogLevel.
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @property
    def value(self) -> int:
        """Gets the integer value of the log level.

        Returns:
            int: The integer value associated with the log level.
        """
        return self._value_

    @property
    def formatted(self) -> str:
        """Gets the formatted string representation of the log level.

        Returns:
            str: The formatted log level, e.g., "DEBUG (10)".
        """
        return f"{self.name} ({self.value})"

    @classmethod
    def get(cls, value: int) -> "LogLevel":
        """Retrieves the LogLevel corresponding to the given integer value.

        Args:
            value (int): The integer value of the desired log level.

        Raises:
            ValueError: If no LogLevel with the given value exists.

        Returns:
            LogLevel: The corresponding LogLevel member.
        """
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"No LogLevel with value {value}")


# Aliases
LogLevel.WARN = LogLevel.WARNING
LogLevel.FATAL = LogLevel.CRITICAL


class ToadLogger:
    """A custom logger with enhanced log levels and optional color support.

    This logger wraps the standard Python `logging` module and integrates with the
    `colorlog` library to provide colored log outputs. It supports various log levels
    defined in the `LogLevel` enumeration.

    Attributes:
        name (str): The name of the logger.
        color (bool): Whether to enable colored log output. Defaults to True.
        level (int): The logging level as an integer.
        logger (logging.Logger): The underlying logger instance.
    """

    DEFAULT_LOG_LEVEL: LogLevel = LogLevel.INFO

    def __init__(
        self,
        name: str,
        level: Optional[Union[int, LogLevel]] = DEFAULT_LOG_LEVEL,
        color: Optional[bool] = True,
    ) -> None:
        """Initializes the ToadLogger with the specified name, level, and color settings.

        Args:
            name (str): The name of the logger.
            level (Optional[Union[int, LogLevel]]): The logging level, either as an integer or a `LogLevel`.
                Defaults to `LogLevel.INFO`.
            color (Optional[bool]): Whether to enable colored log output. Defaults to True.
        """
        self.name: str = name
        self.color: bool = color
        self.level: int = self._validate_level(level)
        self.logger: logging.Logger = self._setup()

    def __getattr__(self, name: str) -> Any:
        """Delegates attribute access to the underlying logger.

        Args:
            name (str): The attribute name.

        Returns:
            Any: The attribute from the underlying logger.
        """
        return getattr(self.logger, name)

    def _setup(self) -> logging.Logger:
        """Sets up the underlying logger with appropriate handlers and formatters.

        Returns:
            logging.Logger: The configured logger instance.
        """
        logger: logging.Logger = (
            colorlog.getLogger(self.name)
            if self.color
            else logging.getLogger(self.name)
        )
        logger.setLevel(self.level)
        handler: logging.Handler = (
            colorlog.StreamHandler() if self.color else logging.StreamHandler()
        )
        handler.setFormatter(self._get_formatter())
        logger.addHandler(handler)
        return logger

    def _get_formatter(self) -> logging.Formatter:
        """Creates and returns a formatter for the log messages.

        Returns:
            logging.Formatter: The configured formatter, with color support if enabled.
        """
        if self.color:
            return colorlog.ColoredFormatter(**self.formatter_params)
        return logging.Formatter(**self.formatter_params)

    @property
    def formatter_params(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """Gets the parameters for the log formatter.

        Returns:
            Dict[str, Union[str, Dict[str, str]]]: The formatter parameters including format strings and color settings.
        """
        params: Dict[str, Union[str, Dict[str, str]]] = {
            "fmt": "%(levelname)s - %(asctime)s  |  %(name)s:  %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
        if self.color:
            params["fmt"] = "%(log_color)s" + params.get("fmt", "")
            params["log_colors"] = {
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            }
        return params

    def _validate_level(self, level: Optional[Union[int, LogLevel]]) -> int:
        """Validates and converts the provided logging level to an integer.

        If the level is not provided or invalid, the default log level is used.

        Args:
            level (Optional[Union[int, LogLevel]]): The logging level to validate.

        Returns:
            int: The validated logging level as an integer.
        """
        setting_default_msg: str = (
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
    # Example usage: LogLevel Enum
    print(f"\n{LogLevel.INFO.value}")  # 20
    print(
        LogLevel.INFO.description
    )  # "Confirmation that things are working as expected."
    print(LogLevel.get(40))  # LogLevel.ERROR
    print(LogLevel.DEBUG.formatted)  # DEBUG (10)
    print(f"{LogLevel.WARN == LogLevel.WARNING}\n")  # True

    # Example usage: Test ToadLogger
    logger: ToadLogger = ToadLogger("toad_logger", LogLevel.DEBUG)
    logger.debug("This is a test debug message.")
    logger.info("This is a test info message.")
    logger.warning("This is a test warning message.")
    logger.error("This is a test error message.")
    logger.critical("This is a test critical message.")
