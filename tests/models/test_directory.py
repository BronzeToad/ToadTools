import logging

import pytest

from toadhub.models import Directory, DirectoryError, DISALLOWED_CHARS
from utils.toad_logger import LogLevel


@pytest.fixture
def frog(mock_toad_logger):
    return mock_toad_logger("test_directory", LogLevel.DEBUG)


@pytest.fixture
def base_directory(mock_folder):
    with mock_folder as mf:
        return Directory(name="test", parent=mf)


@pytest.fixture
def mock_dir(base_directory):
    base_directory.create()
    yield base_directory
    if base_directory.exists:
        base_directory.delete()


def test_directory_error(caplog, frog):
    with caplog.at_level(logging.INFO, logger=frog.name):
        error = DirectoryError("Test error message.", frog)
        assert "Test error message." in caplog.text
        assert error.logger == frog


def test_dir_init(mock_folder, mock_dir):
    assert mock_dir.name == "test"
    assert mock_dir.parent == mock_folder.path
    assert mock_dir.replacement_char is None
    assert mock_dir.disallowed_chars == DISALLOWED_CHARS
    assert mock_dir.path == mock_folder.path / "test"
    assert mock_dir.exists is True


def test_dir_repr(mock_folder, mock_dir):
    expected_repr = (
        f"Directory(name: test, parent: {mock_folder.path}, "
        f"path: {mock_folder.path / 'test'}, exists: True)"
    )
    assert repr(mock_dir) == expected_repr


@pytest.mark.parametrize(
    "name, expected, rep_char",
    [
        ("test", "test", None),
        ("test<dir>", "test_dir", "_"),
        ("test:dir:", "test-dir", "-"),
        (":test<>dir:", "testxxdir", "x"),
    ],
)
def test_dir_name_setter_valid(mock_folder, name, expected, rep_char):
    with mock_folder as mf:
        mock_dir = Directory(name=name, parent=mf, replacement_char=rep_char)
        assert mock_dir.name == expected


def test_dir_name_setter_invalid(mock_folder):
    with mock_folder as mf:
        with pytest.raises(DirectoryError):
            Directory(name="test<dir>", parent=mf)


def test_dir_parent_setter_valid(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test", parent=mf)
        assert mock_dir.parent == mf


def test_dir_parent_setter_invalid():
    with pytest.raises(DirectoryError):
        Directory(name="test", parent="not_a_path")


def test_dir_replacement_char_setter_valid(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test", parent=mf, replacement_char="_")
        assert mock_dir.replacement_char == "_"


def test_dir_replacement_char_setter_invalid(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test<dir>", parent=mf, replacement_char=">")
        assert mock_dir.replacement_char is None
        assert mock_dir.name == "testdir"


@pytest.mark.parametrize(
    "name, char, expected",
    [
        ("testdir>", ">", "testdir"),
        (":test:dir:", ":", "test:dir"),
        ("testdir", ">", "testdir"),
    ],
)
def test_dir_strip_char(mock_folder, name, char, expected):
    assert Directory._strip_char(name, char) == expected


def test_dir_create(mock_dir):
    assert mock_dir.exists is True
    assert mock_dir.path.exists()
    assert mock_dir.path.is_dir()


def test_dir_delete(mock_dir):
    mock_dir.delete()
    assert mock_dir.exists is False
    assert not mock_dir.path.exists()
    assert not mock_dir.path.is_dir()


def test_dir_rename(mock_folder, mock_dir):
    mock_dir.rename("new_test")
    assert mock_dir.name == "new_test"
    assert mock_dir.path == mock_folder.path / "new_test"
    assert mock_dir.exists is True
    assert mock_dir.path.exists()
    assert mock_dir.path.is_dir()


def test_dir_copy(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test", parent=mf)
        mock_dir.create()
        new_parent = mf / "new_parent"
        new_parent.mkdir()
        mock_file = mock_dir.path / "test.txt"
        mock_file.touch()
        assert mock_file.exists()
        assert mock_dir.copy(new_parent)
        new_dir = new_parent / "test"
        assert new_dir.exists()
        assert new_dir.is_dir()
        assert new_dir.parent == new_parent
        assert new_dir.name == "test"
        new_file = new_dir / "test.txt"
        assert new_file.exists()
        assert new_file.is_file()


def test_dir_move(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test", parent=mf)
        mock_dir.create()
        new_parent = mf / "new_parent"
        new_parent.mkdir()
        mock_dir.move(new_parent)
        assert mock_dir.parent == new_parent
        assert mock_dir.path == new_parent / "test"
        assert mock_dir.exists is True
        assert mock_dir.path.exists()
        assert mock_dir.path.is_dir()
