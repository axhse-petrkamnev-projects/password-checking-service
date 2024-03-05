import aiohttp
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PwnedRequester:
    """Pwned API client."""

    PWNED_RANGE_URL = "https://api.pwnedpasswords.com/range/"

    async def request_range(self, hash_prefix: str) -> str:
        """
        Requests the Pwned password leak record range for a hash prefix.

        :param hash_prefix: The hash prefix to query.
        :return: The range as plain text.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.PWNED_RANGE_URL}{hash_prefix}") as resp:
                return (await resp.text()).replace("\r\n", "\n")
