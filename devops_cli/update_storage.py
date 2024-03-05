import argparse

from devops_cli.auxiliary import programs
from devops_cli.auxiliary.utils import (
    NUMERIC_TYPE_INT_OPTIONS,
    REVISION_THREAD_QUANTITY_INT_OPTIONS,
    STORAGE_FILE_QUANTITY_INT_OPTIONS,
    get_numeric_type,
    get_revision_thread_quantity,
    get_storage_file_quantity,
)
from storage.core.models.settings import PwnedStorageSettings

if __name__ == "__main__":
    default_file_quantity = PwnedStorageSettings.DEFAULT_FILE_QUANTITY.value
    default_thread_quantity = (
        PwnedStorageSettings.DEFAULT_REVISION_THREAD_QUANTITY.value
    )
    default_occasion_numeric_type = (
        PwnedStorageSettings.DEFAULT_OCCASION_NUMERIC_TYPE.value
    )

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
        default=default_file_quantity,
        help="The number of files (batches) in which the storage stores its data."
        f" Default: {default_file_quantity}.",
    )
    parser.add_argument(
        "-t",
        "--thread-quantity",
        type=int,
        choices=REVISION_THREAD_QUANTITY_INT_OPTIONS,
        default=default_thread_quantity,
        help="The number of threads to be used for requesting hashed during revision."
        f" Default: {default_thread_quantity}.",
    )
    parser.add_argument(
        "-b",
        "--occasion-numeric-bytes",
        type=int,
        choices=NUMERIC_TYPE_INT_OPTIONS,
        default=default_occasion_numeric_type,
        help="The size of stored leak occasion unsigned number in bytes."
        f" Default: {default_occasion_numeric_type}.",
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
        get_revision_thread_quantity(args.thread_quantity),
        get_numeric_type(args.occasion_numeric_bytes),
        args.mocked,
    )
