import asyncio
import json
from enum import Enum
from json import JSONDecodeError

from storage.auxiliary.action_context_managers import RevisionStepContextManager
from storage.auxiliary.filetools import (
    is_file,
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
from storage.core.models.range_provider import PwnedRangeProvider
from storage.core.models.revision import Revision
from storage.implementations.requester import PwnedRequester


class UpdateResult(Enum):
    """Possible result of an update."""

    IRRELEVANT = "irrelevant"
    DONE = "done"
    FAILED = "failed"


class PwnedStorage:
    """Stores Pwned password leak records."""

    DEFAULT_COROUTINE_NUMBER = 64
    STATE_WAIT_TIME_SECONDS = 0.5
    STATE_FILE = "state.json"

    def __init__(
        self,
        resource_dir: str,
        coroutine_number: int = DEFAULT_COROUTINE_NUMBER,
        range_provider: PwnedRangeProvider = PwnedRequester(),
    ):
        """
        Initialize a new PwnedStorage instance.

        :param resource_dir: The directory where data is stored.
        """
        self.__resource_dir: str = resource_dir
        self.__coroutine_number: int = coroutine_number
        self.__revision: FunctionalRevision = FunctionalRevision()
        self.__range_provider: PwnedRangeProvider = range_provider
        self.__prepared_prefix_amount: int = 0
        self.__revision_step_manager: RevisionStepContextManager = (
            RevisionStepContextManager(self.__revision)
        )
        self.__state: PwnedStorageState = PwnedStorageState()
        self.__state_file_path = join_paths(resource_dir, PwnedStorage.STATE_FILE)
        self.__initialize()

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

    async def get_range(self, prefix: str) -> str:
        """
        Get the Pwned password leak record range for a hash prefix.

        :param prefix: The hash prefix to query.
        :return: The range as plain text.
        """
        prefix = self.__validate_prefix(prefix)
        while self.__revision.is_transiting:
            await self.__wait_a_little()
        self.__state.count_started_request()
        try:
            data_file_path = join_paths(self.__active_dataset_dir, f"{prefix}.txt")
            return read(data_file_path)
        finally:
            self.__state.count_finished_request()

    async def update(self) -> UpdateResult:
        """Perform storage update."""
        if not self.__revision.is_idle:
            return UpdateResult.IRRELEVANT
        self.__revision.indicate_started()
        new_dataset = (self.__state.active_dataset or DatasetID.B).other
        try:
            await self.__update(new_dataset)
        except Exception as error:
            self.__revision.indicate_failed(error)
            await self.__remove_dataset(new_dataset)
        if self.__revision.is_failed:
            return UpdateResult.FAILED
        return UpdateResult.DONE

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

    @staticmethod
    async def __wait_a_little() -> None:
        await asyncio.sleep(PwnedStorage.STATE_WAIT_TIME_SECONDS)

    @property
    def __active_dataset_dir(self) -> str:
        if self.__state.active_dataset is None:
            raise RuntimeError("The storage has no active dataset.")
        return self.__get_dataset_dir(self.__state.active_dataset)

    def __get_dataset_dir(self, dataset: DatasetID) -> str:
        return join_paths(self.__resource_dir, dataset.dir_name)

    async def __update(self, new_dataset: DatasetID) -> None:
        """
        Request an update of all Pwned password leak records.
        :return: The update response status.
        """
        await self.__prepare_new_dataset(new_dataset)
        self.__revision.indicate_prepared()
        while self.__state.has_active_requests:
            await self.__wait_a_little()
        self.__state.mark_to_be_ignored()
        self.__dump_state()
        self.__state.active_dataset = new_dataset
        self.__state.mark_not_to_be_ignored()
        self.__dump_state()
        self.__revision.indicate_transited()
        await self.__remove_dataset(new_dataset.other)
        self.__revision.indicate_completed()

    async def __prepare_new_dataset(self, dataset: DatasetID) -> None:
        dataset_dir = self.__get_dataset_dir(dataset)
        await asyncio.to_thread(lambda: make_empty_dir(dataset_dir))
        await asyncio.gather(
            *[
                self.__prepare_batch(dataset, batch_index)
                for batch_index in range(self.__coroutine_number)
            ]
        )

    async def __prepare_batch(self, dataset: DatasetID, batch_index: int) -> None:
        with self.__revision_step_manager:
            for prefix_index in range(
                batch_index * PWNED_PREFIX_CAPACITY // self.__coroutine_number,
                (batch_index + 1) * PWNED_PREFIX_CAPACITY // self.__coroutine_number,
            ):
                hash_prefix = number_to_hex_code(prefix_index, PWNED_PREFIX_CAPACITY)
                file_path = join_paths(
                    self.__get_dataset_dir(dataset), f"{hash_prefix}.txt"
                )
                write(file_path, await self.__range_provider.get_range(hash_prefix))
                self.__prepared_prefix_amount += 1
                self.__revision.progress = (
                    100 * self.__prepared_prefix_amount // PWNED_PREFIX_CAPACITY
                )

    async def __remove_dataset(self, dataset: DatasetID) -> None:
        try:
            await asyncio.to_thread(lambda: remove_dir(self.__get_dataset_dir(dataset)))
        except Exception as error:
            pass

    def __dump_state(self) -> None:
        state = dict()
        if self.__state.active_dataset is not None:
            state[StoredStateKeys.ACTIVE_DATASET] = self.__state.active_dataset.value
        if self.__state.is_to_be_ignored:
            state[StoredStateKeys.IGNORE_STATE_IN_FILE] = self.__state.is_to_be_ignored
        write(self.__state_file_path, json.dumps(state), overwrite=True)

    def __import_state_from_file(self) -> None:
        if not is_file(self.__state_file_path):
            return
        try:
            state = json.loads(read(self.__state_file_path))
        except JSONDecodeError:
            return
        if not isinstance(state, dict):
            return
        if (
            StoredStateKeys.IGNORE_STATE_IN_FILE in state
            and state[StoredStateKeys.IGNORE_STATE_IN_FILE]
        ):
            return
        if StoredStateKeys.ACTIVE_DATASET in state:
            for dataset in DatasetID:
                if dataset.value == state[StoredStateKeys.ACTIVE_DATASET]:
                    self.__state.active_dataset = dataset

    def __initialize(self) -> None:
        make_dir_if_not_exists(self.__resource_dir)
        self.__import_state_from_file()
