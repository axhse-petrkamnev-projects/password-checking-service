import argparse
import asyncio

from devops_cli.auxiliary import programs
from storage.pwned_storage import PwnedStorage

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Pwned leak record storage.")
    parser.add_argument(
        "resource_dir",
        type=str,
        help="The directory to store data (recommended to be empty).",
    )
    parser.add_argument(
        "-c",
        "--coroutines",
        type=int,
        choices=range(1, 256 + 1),
        default=PwnedStorage.DEFAULT_COROUTINE_NUMBER,
        help="The number of coroutines to be used for requesting hashed during revision."
        f" Default: {PwnedStorage.DEFAULT_COROUTINE_NUMBER}.",
    )
    parser.add_argument(
        "--import_from_file",
        type=str,
        default=None,
        help="The file with sorted hashes to be imported (in the format of the official pwned passwords downloader)."
        " By default the HIBP API is used.",
    )
    parser.add_argument(
        "-m",
        "--mocked",
        action="store_true",
        help="Whether to use a mocked Pwned requester.",
    )

    args = parser.parse_args()
    if args.import_from_file is not None:
        asyncio.run(
            programs.update_storage_from_file(args.resource_dir, args.coroutines, args.import_from_file)
        )
    else:
        asyncio.run(
            programs.update_storage(args.resource_dir, args.coroutines, args.mocked)
        )
