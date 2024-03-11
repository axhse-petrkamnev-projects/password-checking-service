import ssl

import aiohttp
import certifi
import urllib3

from storage.core.models.range_provider import PwnedRangeProvider

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PwnedRequester(PwnedRangeProvider):
    """Pwned API client."""

    PWNED_RANGE_URL = "https://api.pwnedpasswords.com/range/"
    USER_AGENT = {
        "user-agent": "axhse-petrkamnev-password-checking-service",
    }

    async def get_range(self, hash_prefix: str) -> str:
        """
        Requests the Pwned password leak record range for a hash prefix.

        :param hash_prefix: The hash prefix to query.
        :return: The range as plain text.
        """
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        conn = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get(
                f"{self.PWNED_RANGE_URL}{hash_prefix}", headers=self.USER_AGENT
            ) as resp:
                return (await resp.text()).replace("\r\n", "\n")
