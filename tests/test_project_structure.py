import subprocess
from pathlib import Path

import pytest

from src.project_structure import (
    find_project_root, get_git_tracked_files, generate_structured_lines, format_structured_str,
    write_structure_to_file, get_project_structure
)


# ============================================================================================== #

@pytest.fixture
def mock_cwd(monkeypatch, tmp_path):
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    monkeypatch.chdir(project_dir)
    return project_dir


@pytest.fixture
def mock_git_ls_files(monkeypatch):
    calls = []

    def mock_run(*args, **kwargs):
        calls.append((args, kwargs))

        class MockResult:
            stdout = b"file1.py\nfile2.py\nsubdir/file3.py"

        return MockResult()

    monkeypatch.setattr("subprocess.run", mock_run)
    return calls


@pytest.fixture
def mock_root_path(tmp_path):
    return tmp_path / "test_project"


@pytest.fixture
def mock_tracked_files():
    return [
        "file1.py",
        "dir1/file2.py",
        "dir1/subdir/file3.py",
        "dir2/file4.py"
    ]


@pytest.fixture
def mock_project_functions(monkeypatch):
    def mock_find_project_root(project_name):
        return Path("/mock/project/root")

    def mock_get_git_tracked_files(root_path):
        return ["file1.py", "dir1/file2.py"]

    monkeypatch.setattr("src.project_structure.find_project_root", mock_find_project_root)
    monkeypatch.setattr(
        "src.project_structure.get_git_tracked_files",
        mock_get_git_tracked_files
    )


# ============================================================================================== #

@pytest.mark.parametrize("project_name,expected", [
    ("test_project", "test_project"),
    ("TEST_PROJECT", "test_project"),
    ("Test_Project", "test_project"),
])
def test_find_project_root(mock_cwd, project_name, expected):
    result = find_project_root(project_name)
    assert result.name.lower() == expected


def test_find_project_root_not_found(mock_cwd):
    with pytest.raises(NotADirectoryError):
        find_project_root("non_existent_project")


def test_get_git_tracked_files(mock_git_ls_files, tmp_path):
    result = get_git_tracked_files(tmp_path)
    assert result == ["file1.py", "file2.py", "subdir/file3.py"]
    assert len(mock_git_ls_files) == 1
    args, kwargs = mock_git_ls_files[0]
    assert args == (['git', 'ls-files'],)
    assert kwargs['cwd'] == tmp_path
    assert kwargs['stdout'] == subprocess.PIPE


def test_generate_structured_lines(mock_root_path, mock_tracked_files):
    result = generate_structured_lines(mock_root_path, mock_tracked_files)
    expected = [
        str(mock_root_path / "dir1"),
        str(mock_root_path / "dir1/subdir"),
        str(mock_root_path / "dir1/subdir/file3.py"),
        str(mock_root_path / "dir1/file2.py"),
        str(mock_root_path / "dir2"),
        str(mock_root_path / "dir2/file4.py"),
        str(mock_root_path / "file1.py")
    ]
    assert sorted(result, key=lambda s: s.lower()) == sorted(expected, key=lambda s: s.lower())


def test_format_structured_str(mock_root_path):
    structure_lines = [
        str(mock_root_path / "dir1"),
        str(mock_root_path / "dir1/file2.py"),
        str(mock_root_path / "file1.py")
    ]
    result = format_structured_str(mock_root_path, structure_lines)
    expected = "|-- dir1\n|   |-- file2.py\n|-- file1.py\n"
    assert result == expected


def test_write_structure_to_file(mock_root_path, tmp_path):
    output_filename = "test_structure.txt"
    structure_str = "Test structure content"
    write_structure_to_file(tmp_path, output_filename, structure_str)

    output_file = tmp_path / output_filename
    assert output_file.exists()
    assert output_file.read_text() == structure_str


def test_write_structure_to_file_failure(mock_root_path, tmp_path, monkeypatch):
    def mock_open(*args, **kwargs):
        raise PermissionError("Mock permission denied")

    monkeypatch.setattr("builtins.open", mock_open)

    with pytest.raises(FileNotFoundError) as excinfo:
        write_structure_to_file(tmp_path, "test.txt", "content")

    assert "Failed to write project structure to file" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, PermissionError)


def test_get_project_structure(mock_project_functions, capsys):
    get_project_structure("test_project")
    captured = capsys.readouterr()
    assert "|-- file1.py" in captured.out
    assert "|-- dir1" in captured.out
    assert "|   |-- file2.py" in captured.out


def test_get_project_structure_output_to_file(mock_project_functions, tmp_path, monkeypatch):
    monkeypatch.setattr("src.project_structure.write_structure_to_file", lambda *args: None)

    get_project_structure(
        "test_project",
        output_to_file=True,
        output_filename="test_output.txt"
    )
