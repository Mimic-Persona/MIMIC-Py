import os


def read_file(file_path: str) -> str:
    """
    Reads a file and returns its content as a string.
    :param file_path: The path to the text file to be read.
    :return: Content of the text file as a string.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def read_lines(file_path: str) -> list:
    """
    Reads a text file and returns its content as a list of lines.
    :param file_path: The path to the text file to be read.
    :return: List of lines from the text file.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]


def write_file(file_path: str, content: str, overwrite: bool = True):
    """
    Writes content to a file, overwriting it if it already exists.
    :param file_path: The path to the text file to be written.
    :param content: The content to write to the file.
    :param overwrite: If True, overwrites the file if it exists; if False, raises an error if the file exists.
    :return: None
    """
    ensure_dir_exists(os.path.dirname(file_path))
    if not overwrite and os.path.exists(file_path):
        raise FileExistsError(f"File already exists and overwrite is disabled: {file_path}")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[INFO] File written successfully: {file_path}")


def write_lines(file_path: str, lines: list, overwrite: bool = True):
    """
    Writes a list of lines to a text file, overwriting it if it already exists.
    :param file_path: The path to the text file to be written.
    :param lines: The list of lines to write to the file.
    :param overwrite: If True, overwrites the file if it exists; if False, raises an error if the file exists.
    :return: None
    """
    ensure_dir_exists(os.path.dirname(file_path))
    if not overwrite and os.path.exists(file_path):
        raise FileExistsError(f"File already exists and overwrite is disabled: {file_path}")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"[INFO] Lines written successfully to: {file_path}")


def append_file(file_path: str, content: str):
    """
    Appends content to an existing file, or creates the file if it doesn't exist.
    :param file_path: The path to the text file to be appended.
    :param content: The content to append to the file.
    :return: None
    """
    ensure_dir_exists(os.path.dirname(file_path))
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content + '\n')


def file_exists(file_path: str) -> bool:
    """
    Checks if a file exists at the given path.
    :param file_path: The path to the file to check.
    :return: True if the file exists, False otherwise.
    """
    return os.path.isfile(file_path)


def ensure_dir_exists(path: str):
    """
    Ensures that the directory at the given path exists, creating it if necessary.
    :param path: The path to the directory to ensure it exists.
    :return: None
    """
    os.makedirs(path, exist_ok=True)

def recursive_delete(path: str):
    """
    Recursively deletes a file or directory.
    :param path: The path to the file or directory to delete.
    :return: None
    """
    if os.path.isfile(path):
        os.remove(path)

    elif os.path.isdir(path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            recursive_delete(item_path)
        os.rmdir(path)

    else:
        raise FileNotFoundError(f"Path not found: {path}")

    print(f"[INFO] Recursively deleted: {path}")

def get_file_names(directory: str, extension: str = None) -> list:
    """
    Returns a list of file names in the specified directory with an optional file extension filter.
    :param directory: The directory to search for files.
    :param extension: Optional file extension to filter by (e.g., '.txt'). If None, returns all files.
    :return: List of file names in the directory.
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Directory not found: {directory}")

    if extension and not extension.startswith('.'):
        extension = '.' + extension

    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and (not extension or f.endswith(extension))]