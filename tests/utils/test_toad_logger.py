import logging

from utils.toad_logger import ToadLogger, LogLevel


def test_toad_logger_info_message(caplog):
    logger = ToadLogger("test_logger", level=LogLevel.INFO)
    message = "This is a test info message."

    with caplog.at_level(logging.INFO, logger=logger.name):
        logger.info(message)

    # Assert that the message was logged
    assert message in caplog.text

    # Optionally, check the log record details
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "INFO"
    assert record.message == message
    assert record.name == logger.name
