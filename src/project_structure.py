import logging
from pathlib import Path
from typing import Optional, List

from .utils import find_project_root, get_git_tracked_files

log = logging.getLogger(__name__)


def generate_structured_lines(root_path: Path, tracked_files: List[str]) -> List[str]:
    """
    Generates a sorted list of structured lines representing project directory and file structure.

    This function iterates over a list of tracked files, constructing a hierarchical representation
    of directories and files starting from the given root path. Each directory is only added once,
    and the final list is sorted in a case-insensitive manner to ensure a consistent order.

    Parameters:
    - root_path (Path): The root directory of the project from which the structure is generated.
    - tracked_files (List[str]): A list of file paths (as strings) that are tracked by Git.

    Returns:
    - List[str]: A sorted list of strings, each representing a path in the project's structure.
            Directories are included once, and the sorting is case-insensitive.
    """
    log.info("Generating structured representation of project structure...")
    processed_dirs = set()
    structure_lines = []

    for file in tracked_files:
        parts = Path(file).parts
        current_path = root_path

        for i, part in enumerate(parts):
            current_path = current_path / part

            if i == len(parts) - 1:
                structure_lines.append(str(current_path))
            else:
                if current_path not in processed_dirs:
                    structure_lines.append(str(current_path))
                    processed_dirs.add(current_path)

    return sorted(structure_lines, key=lambda s: s.lower())


def format_structured_str(root_path: Path, structure_lines: List[str]) -> str:
    """
    Formats the structured representation of the project's directory and files into a string.

    This function takes a list of paths (both directories and files) and formats them into a
    structured string. Each line in the string represents a path, with indentation representing
    the depth of the path relative to the project root. Directories are appended with a slash to
    distinguish them from files.

    Parameters:
    - root_path (Path): The root directory of the project, used to calculate relative paths.
    - structure_lines (List[str]): A list of strings, each representing a path within the project.

    Returns: - str: A formatted string representing the structure of the project,
        with indentation indicating depth.
    """
    log.info("Formatting project structure output...")
    structure_str = ""

    for line in structure_lines:
        line_path = Path(line)
        relative_path = line_path.relative_to(root_path)
        depth = len(relative_path.parts) - 1
        indent_str = '|   ' * depth

        if line_path.is_dir():
            structure_str += f"{indent_str}|-- {line_path.name}/\n"
        else:
            structure_str += f"{indent_str}|-- {line_path.name}\n"

    return structure_str


def write_structure_to_file(root_path: Path, output_filename: str, structure_str: str) -> None:
    """
    Writes the structured representation of the project to a file.

    This function takes the generated string representation of the project's structure and
    writes it to a specified file. It logs the action of writing to the file and checks if the
    file exists after the attempt to write. If the file does not exist, it logs an error and
    raises a FileNotFoundError.

    Parameters:
    - root_path (Path): The root directory of the project.
    - output_filename (str): The name of the file to which the structure will be written.
    - structure_str (str): The string representation of the project structure.

    Raises:
    - FileNotFoundError: If the file does not exist after attempting to write, or if any other
      error occurs during the write operation. The original exception is set as the __cause__.
    """
    filepath = root_path / output_filename
    log.info(f"Writing project structure to file: {filepath}...")

    try:
        with open(filepath, 'w') as file:
            file.write(structure_str)
            file.close()
    except Exception as e:
        log.error(f"Failed to write project structure to file: {e}")
        raise FileNotFoundError(
            f"Failed to write project structure to file: {filepath}") from e

    if filepath.exists():
        log.info("Project structure successfully written to file.")
    else:
        log.error("Failed to write project structure to file.")
        raise FileNotFoundError(f"Failed to write project structure to file: {filepath}")


def get_project_structure(
        project_name: str,
        output_to_file: bool = False,
        output_filename: Optional[str] = None
):
    """
    Retrieves the structured representation of a project's directory and file structure.

    This function identifies the root path of the project by its name, retrieves all Git-tracked
    files within it, and generates a structured representation of the project's directory and
    file structure. This structured representation can either be printed to the console or
    written to a specified file.

    Parameters: - project_name (str): The name of the project for which the structure is to be
    retrieved. - output_to_file (bool, optional): Flag indicating whether to write the structure
    to a file. Defaults to False. - output_filename (Optional[str], optional): The name of the
    file to which the structure should be written if output_to_file is True. Defaults to
    'project_structure.txt' if not provided.

    Raises:
    - FileNotFoundError: If output_to_file is True and the specified file cannot be written.
    """
    log.info("Getting project structure...")

    if output_to_file and output_filename is None:
        log.warning("Output filename not provided. Defaulting to 'project_structure.txt'")
        output_filename = 'project_structure.txt'

    root_path = find_project_root(project_name)
    tracked_files = get_git_tracked_files(root_path)

    structure_lines = generate_structured_lines(root_path, tracked_files)
    structure_str = format_structured_str(root_path, structure_lines)

    if output_to_file:
        write_structure_to_file(root_path, output_filename, structure_str)
    else:
        log.info("Printing project structure to console...")
        print(structure_str)
