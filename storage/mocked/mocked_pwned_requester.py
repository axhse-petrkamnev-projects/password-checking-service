from hashlib import sha1
from typing import List

from storage.auxiliary.pwned.model import PWNED_PREFIX_LENGTH
from storage.auxiliary.pwned.requester import PwnedRequester


class MockedPwnedRequester(PwnedRequester):
    """Mocked Pwned API client."""

    RECORD_QUANTITY = 1009

    def __init__(self):
        self.__lines: List[str] = [
            sha1(str(index * 397 + 124).encode(encoding="ascii"))
            .hexdigest()[PWNED_PREFIX_LENGTH:]
            .upper()
            + f":{int(sha1(str(index * 82 + 59).encode(encoding='ascii')).hexdigest()[0], 16) + 1}"
            for index in range(self.RECORD_QUANTITY)
        ]
        self.__lines.sort()

    def request_range(self, hash_prefix: str) -> str:
        """
        Requests the Pwned password leak record range for a hash prefix.
        The real range is requested for '00000' prefix.
        Returns artificial non-empty valid ranges for other prefixes.

        :param hash_prefix: The hash prefix to query.
        :return: The range as plain text.
        """
        hash_prefix = hash_prefix.upper()
        if hash_prefix == "00000":
            return super().request_range(hash_prefix)
        num = int(hash_prefix, base=16)
        offset = (num + 3234) % 54347 % (self.RECORD_QUANTITY * 9 // 11 + 1) + 1
        amount = (num + 2832) % 71203 % 8235 % 4 + 1
        return "\n".join(self.__lines[offset : offset + amount])
