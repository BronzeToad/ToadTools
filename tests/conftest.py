import pytest

from utils.toad_logger import ToadLogger


@pytest.fixture
def mock_toad_logger():
    def _mock_frog(name, level):
        return ToadLogger(name, level=level)
    return _mock_frog