import asyncio
import time

from devops_cli.auxiliary.utils import TextStyle, convert_seconds, stylize_text, write
from storage.core.models.revision import Revision
from storage.implementations.file_range_provider import FileRangeImporter
from storage.implementations.mocked_requester import MockedPwnedRequester
from storage.implementations.pwned_storage import PwnedStorage
from storage.implementations.requester import PwnedRequester

CONSOLE_UPDATE_INTERVAL_IN_SECONDS = 1


def __print_revision_progress(revision: Revision, last_status: Revision.Status) -> None:
    """Updates the current status of Pwned storage update."""

    def __get_completion_style(completed: bool) -> TextStyle:
        return TextStyle.GREEN if completed else TextStyle.BLUE

    new_status = revision.status
    if new_status == Revision.Status.NEW:
        return
    if new_status == Revision.Status.FAILED:
        if last_status != Revision.Status.NEW:
            write("\n")
        write(
            stylize_text(f"[FAILED] {revision.error}", [TextStyle.BOLD, TextStyle.RED])
        )
        write("\n")
        return
    console_status = last_status
    if console_status in [Revision.Status.NEW, Revision.Status.PREPARATION]:
        if last_status != Revision.Status.NEW:
            write("\r")
        is_completed = new_status in [
            Revision.Status.TRANSITION,
            Revision.Status.PURGE,
            Revision.Status.COMPLETED,
        ]
        elapsed_seconds = int(time.time()) - revision.start_ts
        style = __get_completion_style(is_completed)
        progress = 100 if is_completed else revision.progress or 0
        write(
            stylize_text(f"[{convert_seconds(elapsed_seconds)}]", TextStyle.PALE_GRAY)
        )
        write(stylize_text(" Prepare new data: ", style))
        write(stylize_text(f"{progress}%", [TextStyle.BOLD, style]))
        if is_completed:
            write("\n")
            console_status = Revision.Status.TRANSITION
    if console_status == Revision.Status.TRANSITION:
        if last_status not in [Revision.Status.NEW, Revision.Status.PREPARATION]:
            write("\r")
        is_completed = new_status in [Revision.Status.PURGE, Revision.Status.COMPLETED]
        style = __get_completion_style(is_completed)
        write(stylize_text("Transit to new prepared data", style))
        if is_completed:
            write("\n")
            console_status = Revision.Status.PURGE
    if console_status == Revision.Status.PURGE:
        if last_status not in [
            Revision.Status.NEW,
            Revision.Status.PREPARATION,
            Revision.Status.TRANSITION,
        ]:
            write("\r")
        is_completed = new_status in [Revision.Status.COMPLETED]
        style = __get_completion_style(is_completed)
        write(stylize_text("Purge old data", style))
        if is_completed:
            write("\n")


async def __watch_update_status(storage: PwnedStorage) -> None:
    last_status = Revision.Status.NEW
    while True:
        revision = storage.revision
        __print_revision_progress(revision, last_status)
        last_status = revision.status
        if last_status in [Revision.Status.COMPLETED, Revision.Status.FAILED]:
            break
        await asyncio.sleep(CONSOLE_UPDATE_INTERVAL_IN_SECONDS)


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
