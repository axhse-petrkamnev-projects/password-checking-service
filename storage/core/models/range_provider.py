from abc import ABC, abstractmethod


class PwnedRangeProvider(ABC):
    """Provides Pwned password leak record ranges"""

    @abstractmethod
    async def get_range(self, hash_prefix: str) -> str:
        """
        Gets the Pwned password leak record range for a hash prefix.

        :param hash_prefix: The hash prefix.
        :return: The range as plain text.
        """
        pass
