import shutil
from pathlib import Path

import pytest

from utils.toad_logger import ToadLogger


@pytest.fixture
def mock_toad_logger():
    def _mock_frog(name, level):
        return ToadLogger(name, level)
    return _mock_frog


class MockFolder:
    def __init__(self):
        self.path = Path(__file__).parent / 'mock'

    def __enter__(self):
        self.path.mkdir(exist_ok=True)
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.path)

@pytest.fixture
def mock_folder():
    return MockFolder()