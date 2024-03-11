from enum import Enum
from typing import Optional


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

    @property
    def dir_name(self) -> str:
        """
        Get the data directory name for the dataset.
        :return: The data directory name.
        """
        return f"hashes-{self.value}"


class PwnedStorageState:
    """Pwned storage state."""

    def __init__(self, active_dataset: Optional[DatasetID] = None):
        """
        Initialize a new PwnedStorageState instance.
        :param active_dataset: The currently active dataset.
        """
        self.__active_dataset: Optional[DatasetID] = active_dataset
        self.__is_to_be_ignored: bool = False
        self.__active_requests: int = 0

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
        """
        self.__active_dataset = value

    @property
    def is_to_be_ignored(self) -> bool:
        """
        Check if the state should be ignored.
        :return: True if the state should be ignored, False otherwise.
        """
        return self.__is_to_be_ignored

    @property
    def has_active_requests(self) -> bool:
        """
        Check if there are active requests.
        :return: True if there are active requests, False otherwise.
        """
        return self.__active_requests > 0

    def count_started_request(self) -> None:
        """Increment the count of active requests."""
        self.__active_requests += 1

    def count_finished_request(self) -> None:
        """Decrement the count of active requests."""
        self.__active_requests -= 1

    def mark_to_be_ignored(self) -> None:
        """Mark the state to be ignored."""
        self.__is_to_be_ignored = True

    def mark_not_to_be_ignored(self) -> None:
        """Mark the state not to be ignored."""
        self.__is_to_be_ignored = False


class StoredStateKeys:
    """Keys used for storing state information."""

    ACTIVE_DATASET = "dataset"
    IGNORE_STATE_IN_FILE = "ignore"
