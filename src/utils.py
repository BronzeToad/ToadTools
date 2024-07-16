import subprocess
from pathlib import Path
from typing import List


def find_project_root(project_name: str) -> Path:
    """
    Finds the root directory of a project by its name.

    This function searches for the project root directory by traversing up from the current
    working directory. It compares each directory's name with the provided project name,
    ignoring case differences. If the root directory is reached without finding a matching
    project name, a NotADirectoryError is raised.

    Parameters:
    - project_name (str): The name of the project to find.

    Returns:
    - Path: The Path object representing the project's root directory.

    Raises:
    - NotADirectoryError: If the project root cannot be found.
    """
    cwd = Path.cwd()
    while cwd.name.lower() != project_name.lower():
        if cwd == cwd.parent:
            raise NotADirectoryError(f"Could not find project root for project: {project_name}")
        cwd = cwd.parent
    return cwd


def get_git_tracked_files(root_path: Path) -> List[str]:
    """
    Retrieves a list of all files tracked by Git in a given project root directory.

    This function executes a Git command to list all files that are currently tracked by Git
    within the specified project root directory. It captures the output, decodes it from bytes
    to a string, and then splits it into a list of file paths.

    Parameters:
    - root_path (Path): The Path object representing the root directory of the project.

    Returns:
    - List[str]: A list of strings, each representing a filepath tracked by Git within the project.
    """
    result = subprocess.run(['git', 'ls-files'], cwd=root_path, stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8').splitlines()
