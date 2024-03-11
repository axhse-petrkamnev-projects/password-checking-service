import asyncio
import time

from devops_cli.auxiliary.utils import TextStyle, convert_seconds, stylize_text, write
from storage.core.models.revision import Revision
from storage.implementations.file_range_provider import FileRangeImporter
from storage.implementations.mocked_requester import MockedPwnedRequester
from storage.implementations.pwned_storage import PwnedStorage
from storage.implementations.requester import PwnedRequester

CONSOLE_UPDATE_INTERVAL_IN_SECONDS = 1


def __print_status(revision: Revision, last_status: Revision.Status) -> None:
    """Updates the current status of Pwned storage update."""

    def __is_completed(status: Revision.Status) -> bool:
        return new_status != status

    def __get_completion_style(status: Revision.Status) -> TextStyle:
        return TextStyle.GREEN if __is_completed(status) else TextStyle.BLUE

    new_status = revision.status
    if new_status == Revision.Status.NEW:
        return
    console_status = last_status
    if console_status in [Revision.Status.NEW, Revision.Status.PREPARATION]:
        if last_status == Revision.Status.PREPARATION:
            write("\r")
        elapsed_seconds = int(time.time()) - revision.start_ts
        is_completed = __is_completed(Revision.Status.PREPARATION)
        style = __get_completion_style(Revision.Status.PREPARATION)
        progress = 100 if is_completed else revision.progress or 0
        write(
            stylize_text(f"[{convert_seconds(elapsed_seconds)}]", TextStyle.PALE_GRAY)
        )
        write(stylize_text(" Prepare new data  ", style))
        write(stylize_text(f"{progress}%", [TextStyle.BOLD, style]))
        if is_completed:
            write("\n")
            console_status = Revision.Status.TRANSITION
    if console_status == Revision.Status.TRANSITION:
        if last_status == Revision.Status.TRANSITION:
            write("\r")
        is_completed = __is_completed(Revision.Status.PREPARATION)
        style = __get_completion_style(Revision.Status.PREPARATION)
        write(stylize_text("Transit to new prepared data", style))
        if is_completed:
            write("\n")
            console_status = Revision.Status.PURGE
    if console_status == Revision.Status.PURGE:
        if last_status == Revision.Status.PURGE:
            write("\r")
        is_completed = __is_completed(Revision.Status.PREPARATION)
        style = __get_completion_style(Revision.Status.PREPARATION)
        write(stylize_text("Purge old data", style))
        if is_completed:
            write("\n")


async def __watch_update_status(storage: PwnedStorage) -> None:
    last_status = Revision.Status.NEW
    if_first_update = True
    while last_status not in [Revision.Status.COMPLETED, Revision.Status.FAILED]:
        if not if_first_update:
            await asyncio.sleep(CONSOLE_UPDATE_INTERVAL_IN_SECONDS)
        if_first_update = False
        revision = storage.revision
        __print_status(revision, last_status)
        last_status = revision.status


async def __update_storage(storage: PwnedStorage) -> None:
    await asyncio.gather(storage.update(), __watch_update_status(storage))


async def update_storage(
    resource_dir: str, coroutines: int, is_requester_mocked: bool
) -> None:
    """Updates the Pwned storage."""
    requester = MockedPwnedRequester() if is_requester_mocked else PwnedRequester()
    storage = PwnedStorage(resource_dir, coroutines, requester)
    await __update_storage(storage)


async def update_storage_from_file(resource_dir: str, data_file_path: str) -> None:
    """Updates the Pwned storage from a file."""
    provider = FileRangeImporter(data_file_path)
    storage = PwnedStorage(resource_dir, 1, provider)
    await __update_storage(storage)
