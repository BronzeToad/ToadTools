from pathlib import Path
from unittest.mock import Mock

import pytest

from src.models.directory import Directory


@pytest.fixture
def mock_directory():
    return Mock(spec=Directory, path=Path("/mock/directory"))
