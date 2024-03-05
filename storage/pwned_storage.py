import json
import time
from concurrent.futures import CancelledError
from concurrent.futures.thread import ThreadPoolExecutor
from enum import Enum

from storage.auxiliary.action_context_managers import (
    ErrorSuppressionContextManager,
    RevisionStepContextManager,
)
from storage.auxiliary.filetools import (
    join_paths,
    make_dir_if_not_exists,
    make_empty_dir,
    read,
    remove_dir,
    write,
)
from storage.auxiliary.models.functional_revision import FunctionalRevision
from storage.auxiliary.models.state import DatasetID, PwnedStorageState, StoredStateKeys
from storage.auxiliary.numeration import number_to_hex_code
from storage.auxiliary.pwned.model import PWNED_PREFIX_CAPACITY
from storage.auxiliary.pwned.record_converter import PwnedRecordConverter
from storage.auxiliary.pwned.record_search import PwnedRecordSearch
from storage.auxiliary.pwned.requester import PwnedRequester
from storage.core.models.revision import Revision
from storage.core.models.settings import PwnedStorageSettings


class UpdateResponse(Enum):
    """Possible response status when requesting an update."""

    STARTED = "started"
    BUSY = "busy"


class UpdateCancellationResponse(Enum):
    """Possible response status when requesting an update cancellation."""

    ACCEPTED = "accepted"
    IRRELEVANT = "irrelevant"


class PwnedStorage:
    """Stores Pwned password leak records."""

    STATE_WAIT_TIME_SECONDS = 0.5
    STATE_FILE = "state.json"

    def __init__(
        self,
        settings: PwnedStorageSettings,
        pwned_requester: PwnedRequester = PwnedRequester(),
    ):
        """
        Initialize a new PwnedStorage instance.

        :param settings: The settings for the storage.
        :param pwned_requester: The instance of Pwned API client.
        """
        self.__settings: PwnedStorageSettings = settings
        self.__revision: FunctionalRevision = FunctionalRevision()
        self.__pwned_requester: PwnedRequester = pwned_requester
        self.__pwned_converter: PwnedRecordConverter = PwnedRecordConverter(
            settings.file_code_length,
            settings.occasion_numeric_bytes,
        )
        self.__record_search: PwnedRecordSearch = PwnedRecordSearch(
            self.__pwned_converter
        )
        self.__state_path = join_paths(self.__settings.resource_dir, self.STATE_FILE)
        self.__state: PwnedStorageState = self.__initialize()
        self.__prepared_prefix_amount: int = 0
        self.__revision_step_manager: RevisionStepContextManager = (
            RevisionStepContextManager(self.__state, self.__revision)
        )

    @property
    def revision(self) -> Revision:
        """
        Get the information related to the most recent update.
        :return: The update-related information.
        """
        return self.__revision.to_dto()

    def get_range(self, prefix: str) -> str:
        """
        Get the Pwned password leak record range for a hash prefix.

        :param prefix: The hash prefix to query.
        :return: The range as plain text.
        """
        prefix = self.__validate_prefix(prefix)
        while True:
            with self.__state.lock:
                is_transiting = self.__revision.is_transiting
                if not is_transiting:
                    self.__state.count_started_request()
            if not is_transiting:
                break
            self.__wait_a_little()
        try:
            return self.__record_search.get_range(prefix, self.__active_dataset_dir)
        finally:
            with self.__state.lock:
                self.__state.count_finished_request()

    def request_update(self) -> UpdateResponse:
        """
        Request an update of all Pwned password leak records.
        :return: The update response status.
        """
        with self.__state.lock:
            if not self.__revision.is_idle:
                return UpdateResponse.BUSY
            self.__revision.indicate_started()
        ThreadPoolExecutor().submit(self.__update)
        return UpdateResponse.STARTED

    def request_update_cancellation(self) -> UpdateCancellationResponse:
        """
        Request an update cancellation.
        :return: The update cancellation response status.
        """
        with self.__state.lock:
            if not self.__revision.is_preparing:
                return UpdateCancellationResponse.IRRELEVANT
            self.__revision.indicate_cancellation()
            return UpdateCancellationResponse.ACCEPTED

    @staticmethod
    def __validate_prefix(prefix: str) -> str:
        if not isinstance(prefix, str):
            raise ValueError("The hash prefix must be a string.")
        prefix = prefix.upper()
        if not all([symbol.isdigit() or symbol in "ABCDEF" for symbol in prefix]):
            raise ValueError("The hash prefix must be a hex string.")
        if len(prefix) < 5 or 6 < len(prefix):
            raise ValueError("The hash prefix must have a length of 5 or 6 symbols.")
        return prefix

    @property
    def __active_dataset_dir(self) -> str:
        if self.__state.active_dataset is None:
            raise RuntimeError("The storage has no active dataset.")
        return self.__get_dataset_dir(self.__state.active_dataset)

    def __get_dataset_dir(self, dataset: DatasetID) -> str:
        return dataset.get_dataset_dir(self.__settings.resource_dir)

    def __update(self) -> None:
        new_active_dataset = (self.__state.active_dataset or DatasetID.B).other
        try:
            self.__prepare_new_dataset(new_active_dataset)
        except Exception as error:
            with ErrorSuppressionContextManager():
                self.__remove_dataset(new_active_dataset)
            if isinstance(error, CancelledError):
                with self.__state.lock:
                    self.__revision.indicate_cancelled()
            else:
                with self.__state.lock:
                    self.__revision.indicate_failed(error)
            return
        with self.__state.lock:
            self.__revision.indicate_prepared()
        while True:
            with self.__state.lock:
                has_active_requests = self.__state.has_active_requests
            if not has_active_requests:
                break
            self.__wait_a_little()
        with self.__state.lock:
            self.__state.mark_to_be_ignored()
        with self.__revision_step_manager:
            self.__dump_state()
        with self.__state.lock:
            self.__state.active_dataset = new_active_dataset
            self.__state.mark_not_to_be_ignored()
        with self.__revision_step_manager:
            self.__dump_state()
        with ErrorSuppressionContextManager():
            self.__remove_dataset(new_active_dataset.other)
        with self.__state.lock:
            self.__revision.indicate_completed()

    def __remove_dataset(self, dataset: DatasetID) -> None:
        remove_dir(dataset.get_dataset_dir(self.__settings.resource_dir))

    def __prepare_new_dataset(self, dataset: DatasetID) -> None:
        dataset_dir = self.__get_dataset_dir(dataset)
        make_empty_dir(dataset_dir)
        self.__prepared_prefix_amount = 0
        for thread_index in range(self.__settings.revision_thread_quantity):
            ThreadPoolExecutor().submit(
                self.__step_batch_preparation, dataset, thread_index
            )
        while True:
            with self.__state.lock:
                if self.__prepared_prefix_amount == PWNED_PREFIX_CAPACITY:
                    break
            self.__wait_a_little()

    def __step_batch_preparation(self, dataset: DatasetID, batch_index: int) -> None:
        with self.__revision_step_manager:
            self.__prepare_batch(dataset, batch_index)

    def __prepare_batch(self, dataset: DatasetID, batch_index: int) -> None:
        dataset_dir = self.__get_dataset_dir(dataset)
        file_quantity = self.__settings.file_quantity
        prefix_group_size = PWNED_PREFIX_CAPACITY // file_quantity
        thread_quantity = self.__settings.revision_thread_quantity
        for file_index in range(
            file_quantity * batch_index // thread_quantity,
            file_quantity * (batch_index + 1) // thread_quantity,
        ):
            self.__assert_preparation_is_not_cancelled()
            file_path = join_paths(
                dataset_dir, f"{number_to_hex_code(file_index, file_quantity)}.dat"
            )
            with open(file_path, "wb") as data_file:
                for prefix_index in range(
                    file_index * prefix_group_size, (file_index + 1) * prefix_group_size
                ):
                    hash_prefix = number_to_hex_code(prefix_index, PWNED_PREFIX_CAPACITY)
                    data_file.write(
                        b"".join(
                            self.__pwned_converter.record_to_bytes(
                                record_row, hash_prefix
                            )
                            for record_row in self.__pwned_requester.get_range(
                                prefix_index
                            ).split()
                        )
                    )
                    with self.__state.lock:
                        self.__prepared_prefix_amount += 1
                        self.__revision.progress = (
                            100 * self.__prepared_prefix_amount // PWNED_PREFIX_CAPACITY
                        )

    def __assert_preparation_is_not_cancelled(self) -> None:
        with self.__state.lock:
            if self.__revision.is_cancelling or self.__revision.is_failed:
                raise CancelledError("Data preparation has been cancelled.")

    def __initialize(self) -> PwnedStorageState:
        with ErrorSuppressionContextManager():
            make_dir_if_not_exists(self.__settings.resource_dir)
        return self.__load_state()

    def __load_state(self) -> PwnedStorageState:
        active_dataset = None
        with ErrorSuppressionContextManager():
            settings = json.loads(read(self.__state_path))
            if not isinstance(settings, dict):
                raise ValueError("Loaded state is not a dictionary.")
            if (
                StoredStateKeys.IGNORE_STATE_IN_FILE in settings
                and settings[StoredStateKeys.IGNORE_STATE_IN_FILE]
            ):
                raise ValueError("Loaded state is marked to be ignored.")
            if StoredStateKeys.ACTIVE_DATASET in settings:
                for dataset_option in DatasetID:
                    if dataset_option.value == settings[StoredStateKeys.ACTIVE_DATASET]:
                        active_dataset = dataset_option
        return PwnedStorageState(active_dataset)

    def __dump_state(self) -> None:
        state = dict()
        if self.__state.active_dataset is not None:
            state[StoredStateKeys.ACTIVE_DATASET] = self.__state.active_dataset.value
        if self.__state.is_to_be_ignored:
            state[StoredStateKeys.IGNORE_STATE_IN_FILE] = self.__state.is_to_be_ignored
        write(self.__state_path, json.dumps(state), overwrite=True)

    def __wait_a_little(self) -> None:
        time.sleep(self.STATE_WAIT_TIME_SECONDS)
