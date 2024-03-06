from storage.auxiliary.models.functional_revision import FunctionalRevision


class RevisionStepContextManager:
    """Context manager for handling revision steps."""

    def __init__(self, revision: FunctionalRevision):
        self.__revision: FunctionalRevision = revision

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if exc_value is not None:
            self.__revision.indicate_failed(exc_value)
            return False
        return True
