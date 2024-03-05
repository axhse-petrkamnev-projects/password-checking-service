import asyncio
import json
import time

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
from storage.auxiliary.pwned.requester import PwnedRequester
from storage.core.models.revision import Revision


class PwnedStorage:
    """Stores Pwned password leak records."""

    STATE_WAIT_TIME_SECONDS = 0.5
    STATE_FILE = "state.json"
    ASYNC_THREAD_NUMBER = 256

    def __init__(self, resource_dir: str):
        """
        Initialize a new PwnedStorage instance.

        :param resource_dir: The directory where data is stored.
        """
        self.__resource_dir: str = resource_dir
        self.__revision: FunctionalRevision = FunctionalRevision()
        self.__pwned_requester: PwnedRequester = PwnedRequester()
        self.__state_path = join_paths(resource_dir, self.STATE_FILE)
        self.__state: PwnedStorageState = self.__initialize()
        self.__prepared_prefix_amount: int = 0
        self.__revision_step_manager: RevisionStepContextManager = (
            RevisionStepContextManager(self.__state, self.__revision)
        )

    @property
    def prepared_prefix_amount(self) -> int:
        return self.__prepared_prefix_amount

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
        data_file_path = join_paths(self.__active_dataset_dir, f"{prefix}.dat")
        return read(data_file_path)

    async def update(self) -> None:
        """
        Request an update of all Pwned password leak records.
        :return: The update response status.
        """
        self.__revision.indicate_started()
        new_active_dataset = (self.__state.active_dataset or DatasetID.B).other
        dataset_dir = self.__get_dataset_dir(new_active_dataset)
        make_empty_dir(dataset_dir)
        self.__prepared_prefix_amount = 0
        await asyncio.gather(
            *[
                self.__prepare_batch(new_active_dataset, batch_index)
                for batch_index in range(self.ASYNC_THREAD_NUMBER)
            ]
        )
        self.__revision.indicate_prepared()
        self.__state.mark_to_be_ignored()
        with self.__revision_step_manager:
            self.__dump_state()
        self.__state.active_dataset = new_active_dataset
        self.__state.mark_not_to_be_ignored()
        with self.__revision_step_manager:
            self.__dump_state()
        with ErrorSuppressionContextManager():
            self.__remove_dataset(new_active_dataset.other)
        self.__revision.indicate_completed()

    @staticmethod
    def __validate_prefix(prefix: str) -> str:
        if not isinstance(prefix, str):
            raise ValueError("The hash prefix must be a string.")
        prefix = prefix.upper()
        if not all([symbol.isdigit() or symbol in "ABCDEF" for symbol in prefix]):
            raise ValueError("The hash prefix must be a hex string.")
        if len(prefix) != 5:
            raise ValueError("The hash prefix must have a length of 5 symbols.")
        return prefix

    @property
    def __active_dataset_dir(self) -> str:
        if self.__state.active_dataset is None:
            raise RuntimeError("The storage has no active dataset.")
        return self.__get_dataset_dir(self.__state.active_dataset)

    def __get_dataset_dir(self, dataset: DatasetID) -> str:
        return dataset.get_dataset_dir(self.__resource_dir)

    def __remove_dataset(self, dataset: DatasetID) -> None:
        remove_dir(dataset.get_dataset_dir(self.__resource_dir))

    async def __prepare_batch(self, dataset: DatasetID, batch_index: int) -> None:
        dataset_dir = self.__get_dataset_dir(dataset)
        with self.__revision_step_manager:
            for prefix_index in range(
                batch_index * PWNED_PREFIX_CAPACITY // self.ASYNC_THREAD_NUMBER,
                (batch_index + 1) * PWNED_PREFIX_CAPACITY // self.ASYNC_THREAD_NUMBER,
            ):
                hash_prefix = number_to_hex_code(prefix_index, PWNED_PREFIX_CAPACITY)
                file_path = join_paths(dataset_dir, f"{hash_prefix}.dat")
                write(
                    file_path, await self.__pwned_requester.request_range(hash_prefix)
                )
                self.__prepared_prefix_amount += 1
                self.__revision.progress = (
                    100 * self.__prepared_prefix_amount // PWNED_PREFIX_CAPACITY
                )

    def __initialize(self) -> PwnedStorageState:
        with ErrorSuppressionContextManager():
            make_dir_if_not_exists(self.__resource_dir)
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
