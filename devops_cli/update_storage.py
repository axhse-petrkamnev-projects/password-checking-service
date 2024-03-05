import argparse
import asyncio

from devops_cli.auxiliary import programs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Pwned leak record storage.")
    parser.add_argument(
        "resource_dir",
        type=str,
        help="The directory to store data (recommended to be empty).",
    )

    args = parser.parse_args()
    asyncio.run(programs.update_storage(args.resource_dir))
