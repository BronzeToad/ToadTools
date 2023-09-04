from pathlib import Path


# =========================================================================== #

def force_extension(filename: str, extension: str) -> str:
    """
    Standardizes the file extension of a given filename.

    This function takes a filename and ensures that it ends with the specified extension.
    The comparison is case-insensitive. If the filename has no extension or has a different
    extension, the specified extension is appended.

    :param filename: The original filename.
    :type filename: str
    :param extension: The extension to force on the filename.
    :type extension: str
    :return: The filename with the standardized extension.
    :rtype: str

    :Example:

    >>> force_extension("file", "json")
    "file.json"

    >>> force_extension("file.JSON", "json")
    "file.JSON"

    >>> force_extension("file.txt", "json")
    "file.txt.json"

    >>> force_extension("file.", "json")
    "file.json"
    """

    normalized_extension = extension.lstrip('.').lower()
    current_extension = Path(filename).suffix.lstrip('.').lower()

    # Handle the case where filename ends with a dot
    if filename.endswith('.'):
        filename = filename.rstrip('.')

    if not current_extension or normalized_extension != current_extension:
        return f"{filename}.{normalized_extension}"

    return filename