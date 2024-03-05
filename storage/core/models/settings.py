from enum import Enum


class StorageFileQuantity(Enum):
    """The number of files (batches) in which the storage stores its data."""

    N_1 = 1
    N_16 = 16
    N_256 = 16**2
    N_4096 = 16**3
    N_65536 = 16**4
    N_1048576 = 16**5


class RevisionThreadQuantity(Enum):
    """The number of threads to be used for requesting hashed during revision."""

    N_1 = 1
    N_16 = 16
    N_256 = 16**2


class NumericType(Enum):
    """Integer numeric types with specific byte size."""

    BYTE = 1
    SHORT = 2
    INTEGER = 4


class PwnedStorageSettings:
    """Settings for PwnedStorage."""

    DEFAULT_FILE_QUANTITY = StorageFileQuantity.N_4096
    DEFAULT_REVISION_THREAD_QUANTITY = RevisionThreadQuantity.N_1
    DEFAULT_OCCASION_NUMERIC_TYPE = NumericType.INTEGER

    def __init__(
        self,
        resource_dir: str,
        file_quantity: StorageFileQuantity = DEFAULT_FILE_QUANTITY,
        revision_thread_quantity: RevisionThreadQuantity = DEFAULT_REVISION_THREAD_QUANTITY,
        occasion_numeric_type: NumericType = DEFAULT_OCCASION_NUMERIC_TYPE,
    ):
        """
        Initialize a new PwnedStorageSettings instance.

        :param resource_dir: The directory path for storing resources.
        :param file_quantity: The number of files (batches) in which the storage stores its data.
        :param revision_thread_quantity: The number of threads to be used for requesting hashed during revision.
        :param occasion_numeric_type: The numeric type used for storing leak occasion values.
        """
        self.__resource_dir: str = resource_dir
        self.__file_quantity: int = file_quantity.value
        self.__revision_thread_quantity: int = revision_thread_quantity.value
        self.__occasion_numeric_bytes: int = occasion_numeric_type.value
        self.__file_code_length: int = self.__calculate_file_code_length()

    @property
    def resource_dir(self) -> str:
        """
        Get the directory path for storing resources.
        :return: The resource directory path.
        """
        return self.__resource_dir

    @property
    def file_quantity(self) -> int:
        """
        Get the quantity of storage files.
        :return: The quantity of storage files.
        """
        return self.__file_quantity

    @property
    def revision_thread_quantity(self) -> int:
        """
        Get the quantity of revision threads.
        :return: The quantity of revision threads.
        """
        return self.__revision_thread_quantity

    @property
    def occasion_numeric_bytes(self) -> int:
        """
        Get the number of bytes used for storing leak occasion values.
        :return: The number of bytes.
        """
        return self.__occasion_numeric_bytes

    @property
    def file_code_length(self) -> int:
        """
        Get the length of data file codes.
        :return: The length of data file codes.
        """
        return self.__file_code_length

    def __calculate_file_code_length(self) -> int:
        code_length = 0
        file_quantity = self.file_quantity - 1
        while file_quantity > 0:
            file_quantity //= 16
            code_length += 1
        return code_length
