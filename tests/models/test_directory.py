import logging

import pytest

from src.models.directory import Directory, DirectoryError, DISALLOWED_CHARS
from utils.toad_logger import LogLevel


@pytest.fixture
def frog(mock_toad_logger):
    return mock_toad_logger("test_directory", LogLevel.DEBUG)


def test_directory_error(caplog, frog):
    with caplog.at_level(logging.INFO, logger=frog.name):
        error = DirectoryError("Test error message.", frog)
        assert "Test error message." in caplog.text
        assert error.logger == frog


def test_dir_init(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test", parent=mf)
        assert mock_dir.name == "test"
        assert mock_dir.parent == mf
        assert mock_dir.replacement_char is None
        assert mock_dir.disallowed_chars == DISALLOWED_CHARS
        assert mock_dir.path == mf / "test"
        assert mock_dir.exists is False


def test_dir_repr(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test", parent=mf)
        expected_repr = (
            f"Directory(name: test, parent: {mf}, "
            f"path: {mf / 'test'}, exists: False)"
        )
        assert repr(mock_dir) == expected_repr


def test_dir_name_setter_valid(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test", parent=mf)
        assert mock_dir.name == "test"


def test_dir_name_setter_with_replacement(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test<dir>", parent=mf, replacement_char="_")
        assert mock_dir.name == "test_dir"


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


def test_dir_strip_char(mock_folder):
    _name = "test>dir>"
    assert Directory._strip_char("testdir>", ">") == "testdir"
    assert Directory._strip_char(":test/dir:", ":") == "test/dir"


def test_dir_create(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test", parent=mf)
        mock_dir.create()
        assert mock_dir.exists is True
        assert mock_dir.path.exists()
        assert mock_dir.path.is_dir()


def test_dir_delete(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test", parent=mf)
        mock_dir.create()
        mock_dir.delete()
        assert mock_dir.exists is False
        assert not mock_dir.path.exists()
        assert not mock_dir.path.is_dir()


def test_dir_rename(mock_folder):
    with mock_folder as mf:
        mock_dir = Directory(name="test", parent=mf)
        assert mock_dir.name == "test"
        mock_dir.create()
        mock_dir.rename("new_test")
        assert mock_dir.name == "new_test"
        assert mock_dir.path == mf / "new_test"
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
