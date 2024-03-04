from storage.auxiliary.models.functional_revision import FunctionalRevision
from storage.auxiliary.models.state import PwnedStorageState


class RevisionStepContextManager:
    """Context manager for handling revision steps."""

    def __init__(self, state: PwnedStorageState, revision: FunctionalRevision):
        self.__state: PwnedStorageState = state
        self.__revision: FunctionalRevision = revision

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if exc_value is not None:
            with self.__state.lock:
                self.__revision.indicate_failed(exc_value)
            return False
        return True


class ErrorSuppressionContextManager:
    """Context manager for suppressing exceptions within a context."""

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        return exc_value is not None
