from enum import Enum
from typing import Optional


class Revision:
    """Update-related information."""

    class Status(Enum):
        """Update status."""

        NEW = "new"

        PREPARATION = "preparation"
        TRANSITION = "transition"
        PURGE = "purge"

        COMPLETED = "completed"
        FAILED = "failed"

    def __init__(
        self,
        status: Status = Status.NEW,
        progress: Optional[int] = None,
        start_ts: Optional[int] = None,
        end_ts: Optional[int] = None,
        error: Optional[Exception] = None,
    ):
        """
        Initialize a new Revision instance.

        :param status: The status of the update.
        :param progress: The progress percentage of the update.
        :param start_ts: The start timestamp of the update.
        :param end_ts: The end timestamp of the update.
        :param error: The error associated with the update.
        """
        self._status: Revision.Status = status
        self._progress: Optional[int] = progress
        self._start_ts: Optional[int] = start_ts
        self._end_ts: Optional[int] = end_ts
        self._error: Optional[Exception] = error

    @property
    def status(self) -> Status:
        """
        Get the status of the update.
        :return: The status of the update.
        """
        return self._status

    @property
    def progress(self) -> Optional[int]:
        """
        Get the progress percentage of the update.
        :return: The progress percentage of the update.
        """
        return self._progress

    @property
    def start_ts(self) -> Optional[int]:
        """
        Get the start timestamp of the update.
        :return: The start timestamp of the update.
        """
        return self._start_ts

    @property
    def end_ts(self) -> Optional[int]:
        """
        Get the end timestamp of the update.
        :return: The end timestamp of the update.
        """
        return self._end_ts

    @property
    def error(self) -> Optional[Exception]:
        """
        Get the error associated with the update.
        :return: The error associated with the update.
        """
        return self._error
