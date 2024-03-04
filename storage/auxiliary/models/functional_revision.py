import time

from storage.core.models.revision import Revision


class FunctionalRevision(Revision):
    def __init__(self):
        """Initialize a new FunctionalRevision instance."""
        super().__init__()

    @property
    def is_idle(self) -> bool:
        """
        Check if the revision is in an idle state.
        :return: True if the revision is idle, False otherwise.
        """
        return self._status in [
            Revision.Status.NEW,
            Revision.Status.COMPLETED,
            Revision.Status.FAILED,
        ]

    @property
    def is_preparing(self) -> bool:
        """
        Check if the revision is in the preparation state.
        :return: True if the revision is preparing, False otherwise.
        """
        return self._status == Revision.Status.PREPARATION

    @property
    def is_transiting(self) -> bool:
        """
        Check if the revision is in the transition state.
        :return: True if the revision is transiting, False otherwise.
        """
        return self._status == Revision.Status.TRANSITION

    @property
    def is_cancelling(self) -> bool:
        """
        Check if the revision is in the cancellation state.
        :return: True if the revision is cancelling, False otherwise.
        """
        return self._status == Revision.Status.CANCELLATION

    @Revision.progress.setter
    def progress(self, value: int) -> None:
        """
        Set the progress percentage of the revision.
        :param value: The progress percentage to set.
        """
        self._progress = value

    def indicate_started(self) -> None:
        """Indicate that the preparation has started."""
        self._start_ts = int(time.time())
        self._end_ts = None
        self._error = None
        self._progress = 0
        self._status = Revision.Status.PREPARATION

    def indicate_prepared(self) -> None:
        """Indicate that the preparation has completed."""
        self._progress = None
        self._status = Revision.Status.TRANSITION

    def indicate_transited(self) -> None:
        """Indicate that the transition has completed."""
        self._status = Revision.Status.PURGE

    def indicate_cancellation(self) -> None:
        """Indicate that the cancellation has started."""
        self._status = Revision.Status.CANCELLATION

    def indicate_completed(self) -> None:
        """Indicate that the revision has completed successfully."""
        self.__set_end_ts()
        self._status = Revision.Status.COMPLETED

    def indicate_cancelled(self) -> None:
        """Indicate that the revision has been cancelled."""
        self.__set_end_ts()
        self._status = Revision.Status.CANCELLED

    def indicate_failed(self, error: Exception) -> None:
        """
        Indicate that the revision has failed with the given error.
        :param error: The error associated with the failure.
        """
        self.__set_end_ts()
        self._error = error
        self._status = Revision.Status.FAILED

    def to_dto(self) -> Revision:
        """
        Convert the FunctionalRevision to a pure Revision instance.

        :return: A Revision instance representing the current state of the revision.
        """
        return Revision(
            self.status,
            self.progress,
            self.start_ts,
            self.end_ts,
            self.error,
        )

    def __set_end_ts(self) -> None:
        self._end_ts = int(time.time())
