from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.models.directory import Directory
from src.models.file import File, FileError


def test_file_initialization(mock_directory):
    """Test the initialization of a File object."""
    file = File("test.txt", mock_directory)
    assert file.name == "test.txt"
    assert file.directory == mock_directory
    assert file.replacement_char is None


def test_file_repr(mock_directory):
    """Test the string representation of a File object."""
    file = File("test.txt", mock_directory)
    expected_repr = (
        f"File(name: test.txt, directory: {mock_directory}, "
        f"path: {mock_directory.path / 'test.txt'}, exists: False)"
    )
    assert repr(file) == expected_repr


@pytest.mark.parametrize(
    "name, expected",
    [
        ("test.txt", "test.txt"),
        (" file with spaces.doc ", "file with spaces.doc"),
        ("file_with_underscore.pdf", "file_with_underscore.pdf"),
    ],
)
def test_file_name_setter_valid(mock_directory, name, expected):
    """Test setting valid file names."""
    file = File(name, mock_directory)
    assert file.name == expected


@pytest.mark.parametrize(
    "name, replacement_char, expected",
    [
        ("file<with>disallowed.txt", "_", "file_with_disallowed.txt"),
        ('file"with:more|disallowed.doc', "-", "file-with-more-disallowed.doc"),
    ],
)
def test_file_name_setter_with_replacement(
    mock_directory, name, replacement_char, expected
):
    """Test setting file names with replacement of disallowed characters."""
    file = File(name, mock_directory, replacement_char)
    assert file.name == expected


@pytest.mark.parametrize(
    "name",
    [
        "file<with>disallowed.txt",
        'file"with:more|disallowed.doc',
    ],
)
def test_file_name_setter_invalid_without_replacement(mock_directory, name):
    """Test setting invalid file names without replacement character."""
    with pytest.raises(FileError):
        File(name, mock_directory)


def test_file_name_setter_reserved(mock_directory):
    """Test setting a reserved file name."""
    with patch("pathlib.Path.is_reserved", return_value=True):
        with pytest.raises(FileError):
            File("CON", mock_directory)


def test_file_directory_setter(mock_directory):
    """Test setting the directory of a File object."""
    file = File("test.txt", mock_directory)
    new_directory = Mock(spec=Directory, path=Path("/new/directory"))
    file.directory = new_directory
    assert file.directory == new_directory


@pytest.mark.parametrize(
    "char, expected",
    [
        ("_", "_"),
        ("-", "-"),
        (None, None),
    ],
)
def test_file_replacement_char_setter_valid(mock_directory, char, expected):
    """Test setting valid replacement characters."""
    file = File("test.txt", mock_directory, replacement_char=char)
    assert file.replacement_char == expected


@pytest.mark.parametrize(
    "char", ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "\0", "ab"]
)
def test_file_replacement_char_setter_invalid(mock_directory, char):
    """Test setting invalid replacement characters."""
    file = File("test.txt", mock_directory, replacement_char=char)
    assert file.replacement_char is None


def test_file_path(mock_directory):
    """Test the path property of a File object."""
    file = File("test.txt", mock_directory)
    expected_path = Path("/mock/directory/test.txt")
    assert file.path == expected_path


@pytest.mark.parametrize(
    "exists, expected",
    [
        (True, False),
        (False, True),
    ],
)
def test_file_delete(mock_directory, exists, expected):
    """Test the File.delete() method."""
    file = File("test.txt", mock_directory)
    with patch(
        "pathlib.Path.is_file", side_effect=[exists, False]
    ):  # First call returns 'exists', second call always returns False
        with patch("pathlib.Path.unlink") as mock_unlink:
            assert file.delete() == expected
            if exists:
                mock_unlink.assert_called_once()


@pytest.mark.parametrize(
    "exists, content, expected",
    [
        (False, "", True),
        (False, "Hello, World!", True),
        (True, "", True),
    ],
)
def test_file_create(mock_directory, exists, content, expected):
    """Test the File.create() method."""
    file = File("test.txt", mock_directory)
    with patch("pathlib.Path.is_file", return_value=exists):
        with patch("pathlib.Path.write_text") as mock_write:
            assert file.create(content) == expected
            if not exists:
                mock_write.assert_called_once_with(content)


def test_file_create_error(mock_directory):
    """Test error handling in File.create() method."""
    file = File("test.txt", mock_directory)
    with patch("pathlib.Path.write_text", side_effect=IOError("Permission denied")):
        with pytest.raises(FileError):
            file.create()


@pytest.mark.parametrize(
    "exists, expected",
    [
        (True, False),
        (False, True),
    ],
)
def test_file_delete(mock_directory, exists, expected):
    """Test the File.delete() method."""
    file = File("test.txt", mock_directory)
    with patch("pathlib.Path.is_file", return_value=exists):
        with patch("pathlib.Path.unlink") as mock_unlink:
            assert file.delete() == expected
            if exists:
                mock_unlink.assert_called_once()


def test_file_delete_error(mock_directory):
    """Test error handling in File.delete() method."""
    file = File("test.txt", mock_directory)
    with patch("pathlib.Path.is_file", return_value=True):
        with patch("pathlib.Path.unlink", side_effect=IOError("Permission denied")):
            with pytest.raises(FileError):
                file.delete()


@pytest.mark.parametrize(
    "new_name, exists, expected",
    [
        ("new.txt", True, True),
        ("test.txt", True, True),
        ("existing.txt", True, False),
    ],
)
def test_file_rename(mock_directory, new_name, exists, expected):
    """Test the File.rename() method."""
    file = File("test.txt", mock_directory)
    with patch("pathlib.Path.is_file", return_value=exists):
        with patch("pathlib.Path.exists", return_value=new_name == "existing.txt"):
            with patch("pathlib.Path.rename") as mock_rename:
                assert file.rename(new_name) == expected
                if expected and new_name != "test.txt":
                    mock_rename.assert_called_once()
                    assert file.name == new_name


def test_file_rename_error(mock_directory):
    """Test error handling in File.rename() method."""
    file = File("test.txt", mock_directory)
    with patch("pathlib.Path.is_file", return_value=True):
        with patch("pathlib.Path.exists", return_value=False):
            with patch("pathlib.Path.rename", side_effect=IOError("Permission denied")):
                with pytest.raises(FileError):
                    file.rename("new.txt")


@pytest.mark.parametrize(
    "file_exists, dest_exists, dest_file_exists, expected",
    [
        (True, True, False, True),
        (False, True, False, False),
        (True, False, False, False),
        (True, True, True, False),
    ],
)
def test_file_move(
    mock_directory, file_exists, dest_exists, dest_file_exists, expected
):
    """Test the File.move() method under various conditions."""
    file = File("test.txt", mock_directory)
    dest_directory = Mock(
        spec=Directory, path=Path("/dest/directory"), exists=dest_exists
    )

    with patch("pathlib.Path.is_file", return_value=file_exists):
        with patch("pathlib.Path.exists", return_value=dest_file_exists):
            with patch("shutil.move") as mock_move:
                result = file.move(dest_directory)
                assert result == expected
                if expected:
                    mock_move.assert_called_once_with(
                        "\\mock\\directory\\test.txt",  # This is the actual source path
                        "\\dest\\directory\\test.txt",  # This is the actual destination path
                    )
                    assert file.directory == dest_directory
                else:
                    mock_move.assert_not_called()


def test_file_move_error(mock_directory):
    """Test error handling in File.move() method."""
    file = File("test.txt", mock_directory)
    dest_directory = Mock(spec=Directory, path=Path("/dest/directory"), exists=True)

    with patch("pathlib.Path.is_file", return_value=True):
        with patch("pathlib.Path.exists", return_value=False):
            with patch("shutil.move", side_effect=IOError("Permission denied")):
                with pytest.raises(FileError):
                    file.move(dest_directory)
