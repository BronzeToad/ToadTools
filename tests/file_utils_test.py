import json
import os
import time
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Generator
from unittest.mock import patch

import pytest

import src.file_utils as fileutils
from src.enum_hatchery import ChecksumType, FileCheckType, FileType, OperationType, SerializationType


# =========================================================================== #

def test_get_file_type_map():
    """Test for get_file_type_map."""
    file_type_map = fileutils.get_file_type_map()
    assert isinstance(file_type_map, dict)
    assert FileType.JSON in file_type_map
    assert file_type_map[FileType.JSON][0] == 'r'


@pytest.mark.parametrize("filepath, check_type, expected_exception", [
    ("existing_file.txt", FileCheckType.EXISTS, FileExistsError),
    ("non_existent_file.txt", FileCheckType.NOT_FOUND, FileNotFoundError),
])
def test_check_filepath(filepath, check_type, expected_exception):
    """Test for check_filepath."""
    with pytest.raises(expected_exception):
        fileutils.check_filepath(Path(filepath), check_type)


@pytest.mark.parametrize("filename, extension, expected", [
    ("file.txt", ".TXT", "file.TXT"),
    ("file", "txt", "file.txt"),
    ("file.", "txt", "file.txt"),
    ("file.txt", ".jpg", "file.jpg"),
])
def test_force_extension(filename, extension, expected):
    """Test for force_extension."""
    assert fileutils.force_extension(filename, extension) == expected


@pytest.mark.parametrize("filename, extension", [
    (None, "txt"),
    ("", "txt"),
    ("file.txt", None),
    ("file.txt", ""),
])
def test_force_extension_invalid_inputs(filename, extension):
    """Test for force_extension with invalid inputs."""
    with pytest.raises(ValueError):
        fileutils.force_extension(filename, extension)


@pytest.mark.parametrize(
    "folder, fname, file_type, find_replace, expected, mock_read_func, mock_content",
    [
        ("/tmp", "test.json", FileType.JSON, None, {"key": "value"}, "json.load", '{"key": "value"}'),
        ("/tmp", "test.html", FileType.HTML, {"<title>": "<heading>"}, "<heading>Test</heading>", "_read_text_file", "<title>Test</title>"),
        ("/tmp", "test.txt", FileType.TXT, {"hello": "world"}, "world", "_read_text_file", "hello"),
        ("/tmp", "test.csv", FileType.CSV, None, [["name", "age"], ["Alice", "30"]], "csv.reader", "name,age\nAlice,30"),
        ("/tmp", "test.yaml", FileType.YAML, None, {"key": "value"}, "yaml.safe_load", "key: value"),
        ("/tmp", "test.xml", FileType.XML, {"<name>": "<username>"}, "<username>John</username>", "_read_text_file", "<name>John</name>"),
        ("/tmp", "test.md", FileType.MD, {"# Title": "## Subtitle"}, "## Subtitle", "_read_text_file", "# Title"),
    ],
)
def test_get_file(folder, fname, file_type, find_replace, expected, mock_read_func, mock_content):
    """Test for get_file."""
    with patch(f"your_module.{mock_read_func}") as mocked_func:
        mocked_func.return_value = mock_content
        assert fileutils.get_file(
            folder=folder,
            filename=fname,
            file_type=file_type,
            find_replace=find_replace,
        ) == expected


@pytest.mark.parametrize("folder, filename", [
    (None, "test.json"),
    ("/tmp", None),
])
def test_get_file_invalid_inputs(folder, filename):
    """Test for get_file with invalid inputs."""
    with pytest.raises(ValueError):
        fileutils.get_file(folder, filename, FileType.JSON)


@pytest.mark.parametrize("src_folder, src_fname, dest_folder, file_type, dest_fname, expected", [
    ("/tmp", "source.json", "/tmp/dest", FileType.JSON, None, "/tmp/dest/source.json"),
    ("/tmp", "source.html", "/tmp/dest", FileType.HTML, "dest.html", "/tmp/dest/dest.html"),
    ("/tmp", "source.csv", "/tmp/dest", FileType.CSV, "dest.csv", "/tmp/dest/dest.csv"),
    ("/tmp", "source.yaml", "/tmp/dest", FileType.YAML, None, "/tmp/dest/source.yaml"),
    ("/tmp", "source.xml", "/tmp/dest", FileType.XML, "dest.xml", "/tmp/dest/dest.xml"),
    ("/tmp", "source.txt", "/tmp/dest", FileType.TXT, "dest.txt", "/tmp/dest/dest.txt"),
    ("/tmp", "source.md", "/tmp/dest", FileType.MD, None, "/tmp/dest/source.md"),
    ("/tmp", "source.ini", "/tmp/dest", FileType.INI, "dest.ini", "/tmp/dest/dest.ini"),
    ("/tmp", "source.log", "/tmp/dest", FileType.LOG, None, "/tmp/dest/source.log"),
    ("/tmp", "source.conf", "/tmp/dest", FileType.CONF, "dest.conf", "/tmp/dest/dest.conf"),
    ("/tmp", "source.py", "/tmp/dest", FileType.PY, None, "/tmp/dest/source.py"),
    ("/tmp", "source.js", "/tmp/dest", FileType.JS, "dest.js", "/tmp/dest/dest.js"),
    ("/tmp", "source.css", "/tmp/dest", FileType.CSS, None, "/tmp/dest/source.css"),
    ("/tmp", "source.jpg", "/tmp/dest", FileType.JPG, "dest.jpg", "/tmp/dest/dest.jpg"),
    ("/tmp", "source.png", "/tmp/dest", FileType.PNG, None, "/tmp/dest/source.png"),
    # ... other test cases for remaining file types ...
])
def test_duplicate_file(src_folder, src_fname, dest_folder, file_type, dest_fname, expected):
    """Test for duplicate_file."""
    with patch('shutil.copy2'):
        assert fileutils.duplicate_file(
            source_folder=src_folder,
            source_filename=src_fname,
            dest_folder=dest_folder,
            file_type=file_type,
            dest_filename=dest_fname
        ) == expected


@pytest.mark.parametrize("src_folder, src_fname, dest_folder", [
    (None, "source.json", "/tmp/dest"),
    ("/tmp", None, "/tmp/dest"),
    ("/tmp", "source.json", None),
])
def test_duplicate_file_invalid_inputs(src_folder, src_fname, dest_folder):
    """Test for duplicate_file with invalid inputs."""
    with pytest.raises(ValueError):
        fileutils.duplicate_file(
            source_folder=src_folder,
            source_filename=src_fname,
            dest_folder=dest_folder,
            file_type=FileType.JSON
        )


def test_delete_file(mocker):
    """Test for delete_file."""
    with TemporaryDirectory() as tmpdir:
        test_file_path = Path(tmpdir) / "test.txt"
        test_file_path.touch()
        mocker.patch('builtins.input', return_value='y')

        result = fileutils.delete_file(
            folder=tmpdir,
            filename="test",
            file_type=FileType.TXT,
            require_confirmation=True
        )

        assert result == True
        assert not test_file_path.exists()


def test_delete_file_cancel(mocker):
    """Test for delete_file with cancel."""
    with TemporaryDirectory() as tmpdir:
        test_file_path = Path(tmpdir) / "test.txt"
        test_file_path.touch()
        mocker.patch('builtins.input', return_value='n')

        result = fileutils.delete_file(
            folder=tmpdir,
            filename="test",
            file_type=FileType.TXT,
            require_confirmation=True
        )

        assert result == False
        assert test_file_path.exists()


def test_rename_file():
    """Test for rename_file"""
    with TemporaryDirectory() as tmpdir:
        src_file_path = Path(tmpdir) / "src.txt"
        dest_file_path = Path(tmpdir) / "dest.txt"
        src_file_path.touch()

        result = fileutils.rename_file(
            src_folder=tmpdir,
            src_filename="src",
            src_file_type=FileType.TXT,
            dest_filename="dest",
            dest_file_type=FileType.TXT
        )

        assert result == str(dest_file_path)
        assert not src_file_path.exists()
        assert dest_file_path.exists()


def test_rename_file_no_overwrite():
    """Test for rename_file with overwrite=False and existing file."""
    with TemporaryDirectory() as tmpdir:
        src_file_path = Path(tmpdir) / "src.txt"
        dest_file_path = Path(tmpdir) / "dest.txt"
        src_file_path.touch()
        dest_file_path.touch()
        with pytest.raises(FileExistsError):
            fileutils.rename_file(
                src_folder=tmpdir,
                src_filename="src",
                src_file_type=FileType.TXT,
                dest_filename="dest",
                dest_file_type=FileType.TXT
            )


def test_rename_file_with_overwrite():
    """Test for rename_file with overwrite=True and existing file."""
    with TemporaryDirectory() as tmpdir:
        src_file_path = Path(tmpdir) / "src.txt"
        dest_file_path = Path(tmpdir) / "dest.txt"
        src_file_path.touch()
        dest_file_path.touch()

        result = fileutils.rename_file(
            src_folder=tmpdir,
            src_filename="src",
            src_file_type=FileType.TXT,
            dest_filename="dest",
            dest_file_type=FileType.TXT,
            overwrite=True
        )

        assert result == str(dest_file_path)
        assert not src_file_path.exists()
        assert dest_file_path.exists()


@pytest.mark.parametrize("folder, flag, expected", [
    ("existing_folder", True, "existing_folder"),
    ("existing_folder", False, "existing_folder"),
    ("non_existent_folder", True, "non_existent_folder"),
    ("non_existent_folder", False, None),
])
def test_ensure_directory_exists(folder, flag, expected):
    """Test for ensure_directory_exists."""
    if expected is not None:
        assert fileutils.ensure_directory_exists(
            folder=folder,
            create_if_missing=flag
        ) == expected
    else:
        assert fileutils.ensure_directory_exists(
            folder=folder,
            create_if_missing=flag
        ) is None


@pytest.mark.parametrize("folder", [
    None,
    "",
])
def test_ensure_directory_exists_invalid_inputs(folder):
    """Test for ensure_directory_exists with invalid inputs."""
    with pytest.raises(ValueError):
        fileutils.ensure_directory_exists(folder)


def test_directory_cleanup(tmpdir):
    """Test for directory_cleanup."""
    directory = tmpdir.mkdir("subdir")

    file1 = directory.join("file1.txt")
    file1.write("content")

    file2 = directory.join("file2.log")
    file2.write("content")

    os.utime(file1, (time.time() - 172800, time.time() - 172800))

    deleted_files_count = fileutils.directory_cleanup(
        directory=str(directory),
        older_than_days=1,
        extensions=['.txt', '.log']
    )

    assert deleted_files_count == 1
    assert not file1.exists()
    assert file2.exists()


@pytest.mark.parametrize("directory", [
    None,
    "",
])
def test_directory_cleanup_invalid_inputs(directory):
    """Test for directory_cleanup with invalid inputs."""
    with pytest.raises(ValueError):
        fileutils.directory_cleanup(directory)


@pytest.mark.parametrize("folder, fname, ftype, expected_size", [
    ("./test_data", "existing_file.txt", None, 1234),
    ("./test_data", "existing_file", FileType.TXT, 1234),
])
def test_get_file_size(folder, fname, ftype, expected_size):
    """Test for get_file_size."""
    assert fileutils.get_file_size(
        folder=folder,
        filename=fname,
        file_type=ftype
    ) == expected_size


@pytest.mark.parametrize("folder, filename", [
    (None, "existing_file.txt"),
    ("", "existing_file.txt"),
    ("./test_data", None),
    ("./test_data", ""),
])
def test_get_file_size_invalid_inputs(folder, filename):
    """Test for get_file_size with invalid inputs."""
    with pytest.raises(ValueError):
        fileutils.get_file_size(folder, filename)


def test_get_file_size_non_existing_file():
    """Test for get_file_size with non-existing file."""
    with pytest.raises(FileNotFoundError):
        fileutils.get_file_size(
            folder="./test_data",
            filename="non_existing_file.txt"
        )


@pytest.mark.parametrize("folder, filename, file_type", [
    ("./test_data", "existing_file.txt", None),
    ("./test_data", "existing_file", FileType.TXT),
])
def test_get_last_modified(folder, filename, file_type):
    """Test for get_last_modified."""
    last_modified = fileutils.get_last_modified(folder, filename, file_type)
    assert isinstance(last_modified, datetime)


@pytest.mark.parametrize("folder, filename", [
    (None, "existing_file.txt"),
    ("", "existing_file.txt"),
    ("./test_data", None),
    ("./test_data", ""),
])
def test_get_last_modified_invalid_inputs(folder, filename):
    """Test for get_last_modified with invalid inputs."""
    with pytest.raises(ValueError):
        fileutils.get_last_modified(folder, filename)


def test_get_last_modified_non_existing_file():
    """Test for get_last_modified with non-existing file."""
    assert fileutils.get_last_modified(
        folder="./test_data",
        filename="non_existing_file.txt"
    ) is None


@pytest.mark.parametrize("folder, fname, exp_type, expected", [
    ("/tmp", "valid_json.json", FileType.JSON, None),
    ("/tmp", "invalid_json.json", FileType.JSON, "Invalid JSON file"),
    ("/tmp", "file.txt", FileType.TXT, "Invalid Text file"),
])
def test_validate_file_type(tmpdir, folder, fname, exp_type, expected):
    """Test for validate_file_type."""
    tmpdir.mkdir(folder)
    # Create test files in tmpdir (left as an exercise) # TODO

    assert fileutils.validate_file_type(
        folder=str(Path(tmpdir) / folder),
        filename=fname,
        expected_type=exp_type
    ) == expected


def test_concatenate_files(tmpdir):
    """Test for concatenate_files."""
    folder = tmpdir.mkdir("folder")
    filenames = ["file1.txt", "file2.txt"]

    for name in filenames:
        path = folder / name
        with open(path, 'w') as f:
            f.write(f"Content of {name}")

    fileutils.concatenate_files(
        folder=str(folder),
        filenames=filenames,
        file_type=FileType.TXT,
        output_filename="output.txt",
        delimiter="\n"
    )

    output_filepath = folder / "output.txt"

    with open(output_filepath, 'r') as f:
        content = f.read()

    assert content == "Content of file1.txt\nContent of file2.txt"


def test_concatenate_files_missing_files(tmpdir):
    """Test for concatenate_files with invalid inputs."""
    with pytest.raises(FileNotFoundError):
        fileutils.concatenate_files(
            folder=str(tmpdir.mkdir("folder")),
            filenames=["missing_file.txt"],
            file_type=FileType.TXT,
            output_filename="output.txt"
        )


@pytest.mark.parametrize("folder, filename, file_type, expected", [
    ("/path/to/folder", "file.txt", FileType.TXT, 10),
    ("/path/to/folder", "image.jpg", FileType.JPG, "Line count is not applicable for binary files")
])
def test_count_lines(folder, filename, file_type, expected):
    """Test for count_lines."""
    assert fileutils.count_lines(folder, filename, file_type) == expected


@pytest.mark.parametrize("folder, filename", [
    (None, "file.txt"),
    ("", "file.txt"),
    ("/path/to/folder", None),
    ("/path/to/folder", ""),
])
def test_count_lines_invalid_inputs(folder, filename):
    """Test for count_lines with invalid inputs."""
    with pytest.raises(ValueError):
        fileutils.count_lines(folder, filename, FileType.TXT)


def test_convert_file_encoding():
    """Test for convert_file_encoding."""
    folder = "/path/to/folder"
    filename = "file.txt"
    file_type = FileType.TXT
    initial_content = fileutils.get_file(folder, filename, file_type)

    fileutils.convert_file_encoding(
        folder=folder,
        filename=filename,
        file_type=file_type,
        target_encoding="utf-8",
        source_encoding="ascii"
    )

    final_content = fileutils.get_file(folder, filename, file_type)

    # Add your assertions here based on what you expect to happen during the conversion   # TODO
    assert initial_content != final_content  # This is just a placeholder   # TODO


@pytest.mark.parametrize("folder, filename", [
    (None, "file.txt"),
    ("", "file.txt"),
    ("/path/to/folder", None),
    ("/path/to/folder", ""),
])
def test_convert_file_encoding_invalid_inputs(folder, filename):
    """Test for convert_file_encoding with invalid inputs."""
    with pytest.raises(ValueError):
        fileutils.convert_file_encoding(
            folder=folder,
            filename=filename,
            file_type=FileType.TXT,
            target_encoding="utf-8"
        )


@pytest.mark.parametrize("folder, fname, qry, regex, cs, ftype, expected", [
    ("/some/folder", "file.txt", "query", False, False, None, ["line with query"]),
    ("/some/folder", "file.txt", "^query$", True, False, None, ["query"]),
    # Add more test cases   # TODO
])
def test_search_text_in_file(folder, fname, qry, regex, cs, ftype, expected):
    """Test for search_text_in_file."""
    assert fileutils.search_text_in_file(
        folder=folder,
        filename=fname,
        query=qry,
        is_regex=regex,
        case_sensitive=cs,
        file_type=ftype
    ) == expected


@pytest.mark.parametrize("folder, filename, query", [
    (None, "file.txt", "query"),
    ("/some/folder", None, "query"),
    ("/some/folder", "file.txt", None),
    # Add more test cases    # TODO
])
def test_search_text_in_file_invalid_inputs(folder, filename, query):
    """Test for search_text_in_file with invalid inputs."""
    with pytest.raises(ValueError):
        fileutils.search_text_in_file(folder, filename, query)


@pytest.mark.parametrize("folder, fname, cs_type, bsize, expected", [
    ("/some/folder", "file.txt", ChecksumType.SHA256, 65536, "expected_checksum"),
    ("/some/folder", "file.txt", ChecksumType.MD5, 65536, "expected_checksum"),
    # Add more test cases    # TODO
])
def test_calculate_checksum(folder, fname, cs_type, bsize, expected):
    """Test for calculate_checksum."""
    assert fileutils.calculate_checksum(
        folder=folder,
        filename=fname,
        checksum_type=cs_type,
        buffer_size=bsize) == expected


@pytest.mark.parametrize("folder, filename", [
    (None, "file.txt"),
    ("/some/folder", None),
    # Add more test cases   # TODO
])
def test_calculate_checksum_invalid_inputs(folder, filename):
    """Test for calculate_checksum with invalid inputs."""
    with pytest.raises(ValueError):
        fileutils.calculate_checksum(folder, filename)


def test_bulk_rename(tmp_path):
    """Test for bulk_rename."""
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "file1.txt").write_text("content")
    (folder / "file2.txt").write_text("content")

    def rename_func(filename):
        return f"new_{filename}"

    fileutils.bulk_rename(
        folder=str(folder),
        rename_func=rename_func
    )

    assert (folder / "new_file1.txt").is_file()
    assert (folder / "new_file2.txt").is_file()


def test_bulk_rename_invalid_folder():
    """Test for bulk_rename with invalid folder."""
    with pytest.raises(NotADirectoryError):
        fileutils.bulk_rename(
            folder="invalid_folder",
            rename_func=lambda x: x
        )


def test_bulk_move_copy(tmp_path):
    """Test for bulk_move_copy."""
    src_folder = tmp_path / "src_folder"
    dest_folder = tmp_path / "dest_folder"
    src_folder.mkdir()
    (src_folder / "file1.txt").write_text("content")
    (src_folder / "file2.txt").write_text("content")

    fileutils.bulk_move_copy(
        src_folder=str(src_folder),
        dest_folder=str(dest_folder),
        filenames=["file1.txt", "file2.txt"],
        operation=OperationType.MOVE
    )

    assert not (src_folder / "file1.txt").is_file()
    assert not (src_folder / "file2.txt").is_file()
    assert (dest_folder / "file1.txt").is_file()
    assert (dest_folder / "file2.txt").is_file()


def test_bulk_move_copy_non_existent_source_file(tmp_path):
    """Test for bulk_move_copy with non-existent source file."""
    src_folder = tmp_path / "src_folder"
    dest_folder = tmp_path / "dest_folder"
    src_folder.mkdir()

    with pytest.raises(FileNotFoundError):
        fileutils.bulk_move_copy(
            src_folder=str(src_folder),
            dest_folder=str(dest_folder),
            filenames=["non_existent.txt"],
            operation=OperationType.MOVE
        )


@patch('your_package.file_utils.FileLock')  # Update import as needed   # FIXME
@patch('your_package.file_utils.get_file')  # Update import as needed   # FIXME
def test_lock_file(mock_get_file, mock_file_lock):
    """Test lock_file."""
    mock_get_file.return_value = "file_content"
    lock_instance = mock_file_lock.return_value

    folder = "test_folder"
    filename = "test_file.txt"
    file_type = FileType.TXT
    find_replace = {"old": "new"}

    result = fileutils.lock_file(
        folder=folder,
        filename=filename,
        file_type=file_type,
        timeout=10,
        find_replace=find_replace
    )

    mock_get_file.assert_called_with(
        folder=folder,
        filename=filename,
        file_type=file_type,
        find_replace=find_replace
    )

    lock_instance.acquire.assert_called()
    assert result == "file_content"


@patch('your_package.file_utils.datetime')  # Update import as needed   # FIXME
@patch('your_package.file_utils.force_extension')  # Update import as needed   # FIXME
@patch('your_package.file_utils.Path')  # Update import as needed   # FIXME
def test_save_versioned_file(mock_path, mock_force_extension, mock_datetime):
    """Test save_versioned_file."""
    mock_force_extension.return_value = "test_file.txt"
    mock_datetime.now.return_value.strftime.return_value = "20220101010101"

    mock_path_instance = mock_path.return_value
    mock_path_instance.glob.return_value = [
        "test_file_20220101010101.txt",
        "test_file_20220101010102.txt",
        "test_file_20220101010103.txt"
    ]

    result = fileutils.save_versioned_file(
        folder="test_folder",
        filename="test_file",
        file_type=FileType.TXT,
        content="Hello, World!",
        timestamp_format="%Y%m%d%H%M%S",
        max_versions=5
    )

    mock_path.assert_called()
    mock_force_extension.assert_called()
    mock_datetime.now.assert_called()
    assert result.endswith("test_file_20220101010101.txt")


@pytest.mark.parametrize("data, serialization_type", [
    ({"key": "value"}, SerializationType.JSON),
    ([1, 2, 3], SerializationType.PICKLE)
])
def test_serialize_deserialize_helper(data, serialization_type):
    """Test for _serialize and _deserialize."""
    with NamedTemporaryFile(delete=False) as temp_file:
        fileutils._serialize(
            data=data,
            filepath=temp_file.name,
            serialization_type=serialization_type
        )
        deserialized_data = fileutils._deserialize(
            filepath=temp_file.name,
            serialization_type=serialization_type
        )

    assert deserialized_data == data


def test_serialize_deserialize_serialize():
    """Test for serialize_deserialize with 'serialize' operation."""
    data = {"key": "value"}

    with NamedTemporaryFile(delete=False) as temp_file:
        fileutils.serialize_deserialize(
            operation="serialize",
            filepath=temp_file.name,
            data=data
        )

        with open(temp_file.name, 'r') as f:
            deserialized_data = json.load(f)

    assert deserialized_data == data


def test_serialize_deserialize_deserialize():
    """Test for serialize_deserialize with 'deserialize' operation."""
    data = {"key": "value"}

    with NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
        json.dump(data, temp_file)
        temp_file.close()
        deserialized_data = fileutils.serialize_deserialize(
            operation="deserialize",
            filepath=temp_file.name
        )

    assert deserialized_data == data


def test_serialize_deserialize_invalid_operation():
    """Test for serialize_deserialize with invalid operation."""
    with pytest.raises(ValueError):
        fileutils.serialize_deserialize(
            operation="invalid_op",
            filepath="some_file"
        )


def test_serialize_deserialize_invalid_filepath():
    """Test for serialize_deserialize with invalid filepath."""
    with pytest.raises(ValueError):
        fileutils.serialize_deserialize(
            operation="serialize",
            filepath="",
            data={"key": "value"}
        )


def test_serialize_deserialize_no_data_serialize():
    """Test for serialize_deserialize without data during serialization."""
    with pytest.raises(ValueError):
        fileutils.serialize_deserialize(
            operation="serialize",
            filepath="some_file.json"
        )


TEMP_FOLDER = "temp_test_folder"
@pytest.fixture(scope="module", autouse=True)
def setup_teardown_temp_folder():
    """Create temporary folder for test files."""
    Path(TEMP_FOLDER).mkdir(exist_ok=True)
    yield
    for temp_file in Path(TEMP_FOLDER).iterdir():
        temp_file.unlink()
    Path(TEMP_FOLDER).rmdir()


def test_read_large_file_in_chunks(setup_teardown_temp_folder):
    """Test for read_large_file_in_chunks."""
    filename = "large_file.txt"
    large_text = "A" * 100

    with open(Path(TEMP_FOLDER) / filename, "w") as f:
        f.write(large_text)

    chunks = fileutils.read_large_file_in_chunks(
        folder=TEMP_FOLDER,
        filename=filename,
        file_type=FileType.TXT,
        chunk_size=10
    )
    assert isinstance(chunks, Generator)

    read_text = "".join(chunk for chunk in chunks)
    assert read_text == large_text


def test_write_large_string_in_chunks(setup_teardown_temp_folder):
    """Test for write_large_string_in_chunks."""
    filename = "large_file_output.txt"
    large_string = "B" * 100

    fileutils.write_large_string_in_chunks(
        folder=TEMP_FOLDER,
        filename=filename,
        file_type=FileType.TXT,
        large_string=large_string,
        chunk_size=10
    )

    with open(Path(TEMP_FOLDER) / filename, "r") as f:
        assert f.read() == large_string
