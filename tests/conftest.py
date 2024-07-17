import pytest
import requests


@pytest.fixture
def mock_response(monkeypatch):
    class MockResponse:
        headers = {"content-length": "50"}  # 5 chunks * 10 bytes each

        def __init__(self):
            self.content_iterator = iter([b"chunk"] * 5)  # 5 chunks

        def iter_content(self, chunk_size=None, decode_unicode=False):
            return self.content_iterator

        def raise_for_status(self):
            pass

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)


@pytest.fixture
def mock_network_error(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.RequestException("Network error")

    monkeypatch.setattr("requests.get", mock_get)
