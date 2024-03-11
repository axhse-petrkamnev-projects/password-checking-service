import asyncio

from storage.auxiliary.action_context_managers import RevisionStepContextManager
from storage.auxiliary.filetools import join_paths, make_empty_dir, read, write
from storage.auxiliary.models.functional_revision import FunctionalRevision
from storage.auxiliary.numeration import number_to_hex_code
from storage.auxiliary.pwned.model import PWNED_PREFIX_CAPACITY
from storage.auxiliary.pwned.requester import PwnedRequester
from storage.core.models.revision import Revision


class PwnedStorage:
    """Stores Pwned password leak records."""

    DATASET_DIR_NAME = "hashes"
    DEFAULT_COROUTINE_NUMBER = 64

    def __init__(
        self,
        resource_dir: str,
        coroutine_number: int = DEFAULT_COROUTINE_NUMBER,
        pwned_requester: PwnedRequester = PwnedRequester(),
    ):
        """
        Initialize a new PwnedStorage instance.

        :param resource_dir: The directory where data is stored.
        """
        self.__resource_dir: str = resource_dir
        self.__coroutine_number: int = coroutine_number
        self.__revision: FunctionalRevision = FunctionalRevision()
        self.__pwned_requester: PwnedRequester = pwned_requester
        self.__prepared_prefix_amount: int = 0
        self.__revision_step_manager: RevisionStepContextManager = (
            RevisionStepContextManager(self.__revision)
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
        data_file_path = join_paths(self.__dataset_dir, f"{prefix}.dat")
        return read(data_file_path)

    async def update(self) -> None:
        """
        Request an update of all Pwned password leak records.
        :return: The update response status.
        """
        self.__revision.indicate_started()
        make_empty_dir(self.__dataset_dir)
        self.__prepared_prefix_amount = 0
        await asyncio.gather(
            *[
                self.__prepare_batch(batch_index)
                for batch_index in range(self.__coroutine_number)
            ]
        )
        self.__revision.indicate_prepared()
        self.__revision.indicate_completed()

    async def update_with_file(self, filename: str) -> None:
        """
        Request an update of all Pwned password leak records.

        :param filename: The path to the file that contains the prefixes.
        :return: The update response status.
        """
        self.__revision.indicate_started()
        make_empty_dir(self.__dataset_dir)
        self.__prepared_prefix_amount = 0
        await asyncio.gather(
            *[
                self.__prepare_batch_file(batch_index)
                for batch_index in range(self.__coroutine_number)
            ]
        )
        self.__revision.indicate_prepared()
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
    def __dataset_dir(self) -> str:
        return join_paths(self.__resource_dir, self.DATASET_DIR_NAME)

    async def __prepare_batch(self, batch_index: int) -> None:
        with self.__revision_step_manager:
            for prefix_index in range(
                batch_index * PWNED_PREFIX_CAPACITY // self.__coroutine_number,
                (batch_index + 1) * PWNED_PREFIX_CAPACITY // self.__coroutine_number,
            ):
                hash_prefix = number_to_hex_code(prefix_index, PWNED_PREFIX_CAPACITY)
                file_path = join_paths(self.__dataset_dir, f"{hash_prefix}.txt")
                write(
                    file_path, await self.__pwned_requester.request_range(hash_prefix)
                )
                self.__prepared_prefix_amount += 1
                self.__revision.progress = (
                    100 * self.__prepared_prefix_amount // PWNED_PREFIX_CAPACITY
                )

    @staticmethod
    async def __find_lines_with_prefix(filename, prefix):
        def find_offset(start, end):
            nonlocal filename, prefix
            while start + 1 < end:
                mid = (start + end) // 2
                f.seek(mid)
                f.readline() # Skip possibly partial line
                line = f.readline().decode('utf-8')
                if not line:
                    break # EOF
                line_prefix = line[:5]
                if line_prefix < prefix:
                    start = mid
                else:
                    end = mid
            if start != 0:
                return end
            return start

        results = []
        with open(filename, 'rb') as f:
            # Find start offset of the prefix
            start_offset = find_offset(0, f.seek(0, 2))

            # Read and process the lines between the found offsets
            f.seek(start_offset)
            if start_offset != 0:
                f.readline()
            while True:
                line = f.readline().decode('utf-8').strip()
                if not line or not line.startswith(prefix):
                    break
                results.append(line[5:])

        return '\n'.join(results)

    async def __prepare_batch_file(self, batch_index: int, filename: str) -> None:
        with self.__revision_step_manager:
            for prefix_index in range(
                batch_index * PWNED_PREFIX_CAPACITY // self.__coroutine_number,
                (batch_index + 1) * PWNED_PREFIX_CAPACITY // self.__coroutine_number,
            ):
                hash_prefix = number_to_hex_code(prefix_index, PWNED_PREFIX_CAPACITY)
                file_path = join_paths(self.__dataset_dir, f"{hash_prefix}.txt")
                write(
                    file_path, await self.__find_lines_with_prefix(filename, hash_prefix)
                )
                self.__prepared_prefix_amount += 1
                self.__revision.progress = (
                    100 * self.__prepared_prefix_amount // PWNED_PREFIX_CAPACITY
                )
