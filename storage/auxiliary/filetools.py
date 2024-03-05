import os
import shutil
from enum import Enum
from typing import List, Optional, Union


class Encoding(Enum):
    """Commonly used encodings."""

    UTF_8: str = "utf-8"
    ASCII: str = "ascii"


def join_paths(*paths: str) -> str:
    """
    Join multiple path components into a single path.

    :param paths: Path components.
    :return: Joined path.
    """
    return os.path.join(*paths)


def is_dir(path: str) -> bool:
    """
    Check if a directory exists.

    :param path: The path to the directory.
    :return: True if the directory exists, False otherwise.
    """
    return os.path.exists(path) and os.path.isdir(path)


def clear_dir(path: str) -> None:
    """
    Clear all files and subdirectories in a directory.

    :param path: Directory path.
    """
    if os.path.isdir(path):
        _, dir_paths, file_paths = next(os.walk(path))
        for dir_path in dir_paths:
            shutil.rmtree(join_paths(path, dir_path))
        for file_path in file_paths:
            os.remove(join_paths(path, file_path))


def make_dir_if_not_exists(path: str) -> None:
    """
    Create a directory if it does not exist.

    :param path: Directory path.
    """
    if not is_dir(path):
        os.mkdir(path)


def make_empty_dir(path: str) -> None:
    """
    Create an empty directory by first making sure it exists and then clearing it.

    :param path: Directory path.
    """
    make_dir_if_not_exists(path)
    clear_dir(path)


def remove_dir(path: str) -> None:
    """
    Remove a directory and its content.

    :param path: Directory path.
    """
    if os.path.isdir(path):
        shutil.rmtree(path)


def read(path: str, binary=False, encoding: Optional[Encoding] = None) -> str:
    """
    Read the contents of a file.

    :param path: File path.
    :param binary: Whether to open the file in binary mode.
    :param encoding: File encoding.
    :return: Contents of the file.
    """
    mode = "rb" if binary else "r"
    encoding = encoding and encoding.value
    with open(path, mode, encoding=encoding) as file:
        return file.read()


def write(
    path: str,
    lines: Union[str, List[str]],
    overwrite=False,
    encoding: Encoding = Encoding.ASCII,
) -> None:
    """
    Write lines to a file.

    :param path: File path.
    :param lines: Lines to write (either a string or a list of strings).
    :param overwrite: Whether to overwrite the file (default is False).
    :param encoding: File encoding.
    """
    mode = "w" if overwrite else "a"
    with open(path, mode, encoding=encoding.value) as file:
        if isinstance(lines, str):
            file.write(lines)
        else:
            file.writelines(lines)
