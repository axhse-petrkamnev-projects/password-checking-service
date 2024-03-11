import asyncio
from typing import List

from storage.auxiliary import hasher
from storage.auxiliary.pwned.model import PWNED_PREFIX_LENGTH
from storage.implementations.requester import PwnedRequester


class MockedPwnedRequester(PwnedRequester):
    """Mocked Pwned API client."""

    RECORD_QUANTITY = 1009
    INCLUDED_PASSWORDS = [
        ("hello", 273646),
        ("hello12345678901", 10),
        ("superstronger", 1),
        ("123_56789", 3),
    ]

    def __init__(self):
        self.__records: List[str] = [
            hasher.sha1(str(index * 397 + 124))[PWNED_PREFIX_LENGTH:]
            + f":{int(hasher.sha1(str(index * 82 + 59))[0], 16) + 1}"
            for index in range(self.RECORD_QUANTITY)
        ]
        self.__records.sort()
        self.__extra_records = dict()
        for password, occasion_number in self.INCLUDED_PASSWORDS:
            password_hash = hasher.sha1(password)
            record = f"{password_hash[5:]}:{occasion_number}"
            self.__extra_records.setdefault(password_hash[:5], list())
            self.__extra_records[password_hash[:5]].append(record)

    async def request_range(self, hash_prefix: str) -> str:
        hash_prefix = hash_prefix.upper()
        if hash_prefix == "00000":
            return await super().get_range(hash_prefix)
        await asyncio.sleep(0)
        num = int(hash_prefix, base=16)
        offset = (num + 3234) % 54347 % (self.RECORD_QUANTITY * 9 // 11 + 1) + 1
        amount = (num + 2832) % 71203 % 8235 % 4 + 1
        records = self.__records[offset : offset + amount]
        if hash_prefix in self.__extra_records:
            records.extend(self.__extra_records[hash_prefix])
            records.sort()
        return "\n".join(records)
