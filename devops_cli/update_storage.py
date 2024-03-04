import argparse

from devops_cli.auxiliary import programs
from devops_cli.auxiliary.utils import (
    NUMERIC_TYPE_INT_OPTIONS,
    STORAGE_FILE_QUANTITY_INT_OPTIONS,
    get_numeric_type,
    get_storage_file_quantity,
)
from storage.core.models.settings import NumericType, StorageFileQuantity

DEFAULT_STORAGE_FILE_INT_QUANTITY: int = StorageFileQuantity.N_4096.value
DEFAULT_OCCASION_NUMERIC_INT_TYPE: int = NumericType.INTEGER.value

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Pwned leak record storage.")
    parser.add_argument(
        "-r",
        "--resource-dir",
        type=str,
        help="The directory to store data (recommended to be empty).",
    )
    parser.add_argument(
        "-f",
        "--file-quantity",
        type=int,
        choices=STORAGE_FILE_QUANTITY_INT_OPTIONS,
        default=DEFAULT_STORAGE_FILE_INT_QUANTITY,
        help="The number of files (batches) in which the storage stores its data."
        f" Default: {DEFAULT_STORAGE_FILE_INT_QUANTITY}.",
    )
    parser.add_argument(
        "-b",
        "--occasion-numeric-bytes",
        type=int,
        choices=NUMERIC_TYPE_INT_OPTIONS,
        default=DEFAULT_OCCASION_NUMERIC_INT_TYPE,
        help="The size of stored leak occasion unsigned number in bytes."
        f" Default: {DEFAULT_OCCASION_NUMERIC_INT_TYPE}.",
    )
    parser.add_argument(
        "-m",
        "--mocked",
        action="store_true",
        help="Whether to use a mocked Pwned requester.",
    )

    args = parser.parse_args()
    programs.update_storage(
        args.resource_dir,
        get_storage_file_quantity(args.file_quantity),
        get_numeric_type(args.occasion_numeric_bytes),
        args.mocked,
    )
