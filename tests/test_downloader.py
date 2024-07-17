import pytest
import requests

from src.downloader import create_progress_bar, download_file, download_multiple


@pytest.mark.parametrize("percent,width,expected", [
    (0, 10, "|----------| 0%"),
    (50, 10, "|█████-----| 50%"),
    (100, 10, "|██████████| 100%"),
])
def test_create_progress_bar(percent, width, expected):
    assert create_progress_bar(percent, width) == expected


def test_download_file(mock_response, tmp_path):
    download_file("https://example.com/file", tmp_path, "test_file.txt")

    assert (tmp_path / "test_file.txt").exists()
    assert (tmp_path / "test_file.txt").read_bytes() == b"chunk" * 5


def test_download_file_with_status_bar(mock_response, tmp_path, capsys):
    download_file("https://example.com/file", tmp_path, "test_file.txt", status_bar=True)

    captured = capsys.readouterr()
    assert "test_file.txt: |" in captured.out
    assert "%" in captured.out
    assert (tmp_path / "test_file.txt").exists()
    assert (tmp_path / "test_file.txt").read_bytes() == b"chunk" * 5


def test_download_file_existing(mock_response, tmp_path):
    existing_file = tmp_path / "existing_file.txt"
    existing_file.touch()

    download_file("https://example.com/file", tmp_path, "existing_file.txt")

    assert existing_file.read_bytes() == b""  # File should not have been overwritten


def test_download_file_network_error(mock_network_error, tmp_path):
    with pytest.raises(requests.RequestException, match="Network error"):
        download_file("https://example.com/file", tmp_path, "test_file.txt")


@pytest.fixture
def mock_download_file(monkeypatch):
    calls = []

    def mock_download(*args, **kwargs):
        calls.append((args, kwargs))

    monkeypatch.setattr("src.downloader.download_file", mock_download)
    return calls


def test_download_multiple(mock_download_file, tmp_path):
    urls = ["https://example.com/file1", "https://example.com/file2"]

    download_multiple(urls, tmp_path)

    assert len(mock_download_file) == 2
    assert mock_download_file[0][0] == ("https://example.com/file1", tmp_path, "file1", False)
    assert mock_download_file[1][0] == ("https://example.com/file2", tmp_path, "file2", False)


def test_download_multiple_with_custom_filename(mock_download_file, tmp_path):
    urls = ["https://example.com/file1"]

    def _filename_function(url):
        return "custom_" + url.split("/")[-1]

    download_multiple(urls, tmp_path, _filename_function)

    assert len(mock_download_file) == 1
    assert mock_download_file[0][0] == (
        "https://example.com/file1", tmp_path, "custom_file1", False)


def test_download_multiple_with_error(monkeypatch, tmp_path):
    calls = []

    def mock_download(*args, **kwargs):
        calls.append((args, kwargs))
        if len(calls) == 2:
            raise Exception("Download error")

    monkeypatch.setattr("src.downloader.download_file", mock_download)

    urls = ["https://example.com/file1", "https://example.com/file2"]
    download_multiple(urls, tmp_path)

    assert len(calls) == 2


def test_download_multiple_empty_list(tmp_path):
    download_multiple([], tmp_path)
    assert len(list(tmp_path.iterdir())) == 0
