import subprocess

import pytest

from src.utils import find_project_root, get_git_tracked_files


# ============================================================================================== #

@pytest.fixture
def mock_cwd(monkeypatch, tmp_path):
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    monkeypatch.chdir(project_dir)
    return project_dir


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


# ============================================================================================== #

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


def test_get_git_tracked_files(mock_git_ls_files, tmp_path):
    result = get_git_tracked_files(tmp_path)
    assert result == ["file1.py", "file2.py", "subdir/file3.py"]
    assert len(mock_git_ls_files) == 1
    args, kwargs = mock_git_ls_files[0]
    assert args == (['git', 'ls-files'],)
    assert kwargs['cwd'] == tmp_path
    assert kwargs['stdout'] == subprocess.PIPE
