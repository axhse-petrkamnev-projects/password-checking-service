from enum import Enum
from typing import Optional

from storage.auxiliary.filetools import join_paths


class DatasetID(Enum):
    """Dataset identification."""

    A = "a"
    B = "b"

    @property
    def other(self) -> "DatasetID":
        """
        Get the other dataset.
        :return: The other dataset.
        """
        return DatasetID.B if self == DatasetID.A else DatasetID.A

    def get_dataset_dir(self, resource_dir: str) -> str:
        """
        Get the data directory path for the dataset.

        :param resource_dir: The resource directory.
        :return: The data directory path.
        """
        return join_paths(resource_dir, f"dataset_{self.value}")


class PwnedStorageState:
    """Pwned storage state."""

    def __init__(self, active_dataset: Optional[DatasetID] = None):
        """
        Initialize a new PwnedStorageState instance.
        :param active_dataset: The currently active dataset.
        """
        self.__active_dataset: Optional[DatasetID] = active_dataset
        self.__is_to_be_ignored: bool = False

    @property
    def active_dataset(self) -> Optional[DatasetID]:
        """
        Get the currently active dataset.
        :return: The active dataset.
        """
        return self.__active_dataset

    @active_dataset.setter
    def active_dataset(self, value: Optional[DatasetID]) -> None:
        """
        Set the currently active dataset.

        :param value: The dataset to set as active.
        :return: None
        """
        self.__active_dataset = value

    @property
    def is_to_be_ignored(self) -> bool:
        """
        Check if the state should be ignored.
        :return: True if the state should be ignored, False otherwise.
        """
        return self.__is_to_be_ignored

    def mark_to_be_ignored(self) -> None:
        """
        Mark the state to be ignored.
        :return: None
        """
        self.__is_to_be_ignored = True

    def mark_not_to_be_ignored(self) -> None:
        """
        Mark the state not to be ignored.
        :return: None
        """
        self.__is_to_be_ignored = False


class StoredStateKeys:
    """Keys used for storing state information."""

    ACTIVE_DATASET = "dataset"
    IGNORE_STATE_IN_FILE = "ignore"
