from enum import Enum, auto
from typing import BinaryIO

from storage.auxiliary.filetools import join_paths
from storage.auxiliary.pwned.record_converter import PwnedRecordConverter


class PwnedRecordSearch:
    """Pwned data file search."""

    class Boundary(Enum):
        LEFT = auto()
        RIGHT = auto()

    def __init__(self, pwned_converter: PwnedRecordConverter):
        self.__converter: PwnedRecordConverter = pwned_converter

    def get_range(self, hash_prefix: str, active_dataset_dir: str) -> str:
        """
        Retrieve the Pwned password leak record range from file for a hash prefix.

        :param hash_prefix: The hash prefix.
        :param active_dataset_dir: The directory path for the currently used dataset.
        :return: The range as plain text.
        """
        file_code = hash_prefix[: self.__converter.dropped_prefix_length]
        desired_stored_bytes = self.__converter.desired_stored_prefix_bytes(hash_prefix)
        has_desired_stored_prefix_odd_length = (
            self.__converter.has_desired_stored_prefix_odd_length(hash_prefix)
        )
        data_file_path = join_paths(active_dataset_dir, f"{file_code}.dat")
        with open(data_file_path, "rb") as data_file:
            left_index = self.__find_boundary(
                desired_stored_bytes,
                has_desired_stored_prefix_odd_length,
                data_file,
                PwnedRecordSearch.Boundary.LEFT,
            )
            right_index = self.__find_boundary(
                desired_stored_bytes,
                has_desired_stored_prefix_odd_length,
                data_file,
                PwnedRecordSearch.Boundary.RIGHT,
            )
            return self.__load_range(left_index, right_index, file_code, data_file)

    def __load_range(
        self, left_index: int, right_index: int, dropped_prefix: str, file: BinaryIO
    ) -> str:
        rows = list()
        for index in range(left_index, right_index):
            file.seek(self.__converter.record_size * index)
            record_bytes = file.read(self.__converter.record_size)
            rows.append(
                self.__converter.record_from_bytes(record_bytes, dropped_prefix)
            )
        return "\n".join(rows)

    def __find_boundary(
        self,
        desired_stored_bytes: bytes,
        has_desired_stored_prefix_odd_length: bool,
        file: BinaryIO,
        boundary: Boundary,
    ) -> int:
        record_size = self.__converter.record_size
        prefix_beginning_size = len(desired_stored_bytes)
        left = 0
        right = 1
        file.seek(0)
        while file.read(1):
            right *= 2
            file.seek(record_size * right)
        while left < right:
            mid = (left + right) // 2
            file.seek(record_size * mid)
            if not file.read(1):
                right = mid
                continue
            file.seek(record_size * mid)
            beginning_bytes = file.read(prefix_beginning_size)
            if has_desired_stored_prefix_odd_length:
                beginning_bytes = bytearray(beginning_bytes)
                beginning_bytes[-1] = beginning_bytes[-1] // 16 * 16
            is_left_to_shift = (
                beginning_bytes < desired_stored_bytes
                if boundary == boundary.LEFT
                else beginning_bytes <= desired_stored_bytes
            )
            if is_left_to_shift:
                left = mid + 1
            else:
                right = mid
        return left
