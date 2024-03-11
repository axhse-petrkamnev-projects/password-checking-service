import tempfile

import pytest

from storage.auxiliary.filetools import join_paths, make_empty_dir


@pytest.fixture(scope="session")
def temp_dir() -> str:
    temp_dir_path = join_paths(tempfile.gettempdir(), f"pwned-storage-tests")
    make_empty_dir(temp_dir_path)
    return temp_dir_path
