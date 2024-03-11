import asyncio

import pytest

from storage.auxiliary import hasher
from storage.auxiliary.filetools import join_paths, make_empty_dir
from storage.core.models.revision import Revision
from storage.implementations.mocked_requester import MockedPwnedRequester
from storage.implementations.pwned_storage import PwnedStorage
from tests.shared import temp_dir


@pytest.fixture(scope="session")
def storage(temp_dir: str) -> PwnedStorage:
    resource_dir = join_paths(temp_dir, "storage")
    make_empty_dir(resource_dir)
    return PwnedStorage(resource_dir, 1, MockedPwnedRequester())


@pytest.fixture(scope="session")
def updated_storage(storage: PwnedStorage) -> PwnedStorage:
    asyncio.run(storage.update())
    assert storage.revision.status == Revision.Status.COMPLETED
    return storage


@pytest.mark.asyncio
async def test_ranges(updated_storage: PwnedStorage):
    prefixes_to_check = ["FADED", "Faded", "F" * 5]
    for prefix in prefixes_to_check:
        found_range = await updated_storage.get_range(prefix)
        requested_range = await MockedPwnedRequester().get_range(prefix)
        assert found_range == requested_range
    found_range = await updated_storage.get_range("0" * 5)
    requested_range = await MockedPwnedRequester().get_range("0" * 5)
    assert len(found_range) == len(requested_range)
    assert found_range.count("\n") == requested_range.count("\n")
    assert found_range[:100] == requested_range[:100]
    assert (
        found_range[len(found_range) // 2 : len(found_range) // 2 + 100]
        == requested_range[len(found_range) // 2 : len(found_range) // 2 + 100]
    )
    assert found_range[-100:] == requested_range[-100:]


@pytest.mark.asyncio
async def test_leak_check(updated_storage: PwnedStorage):
    for password, occasion in MockedPwnedRequester.INCLUDED_PASSWORDS:
        password_hash = hasher.sha1(password)
        records1 = (await updated_storage.get_range(password_hash[:5])).split()
        records2 = (await updated_storage.get_range(password_hash[:6])).split()
        expected_record = f"{password_hash[5:]}:{occasion}"
        assert expected_record in records1
        assert expected_record in records2
    for password, occasion in MockedPwnedRequester.INCLUDED_PASSWORDS:
        password += "_"
        password_hash = hasher.sha1(password)
        records1 = await updated_storage.get_range(password_hash[:5])
        records2 = await updated_storage.get_range(password_hash[:6])
        not_expected_suffix = password_hash[5:]
        assert not_expected_suffix not in records1
        assert not_expected_suffix not in records2
