import time

import requests
import urllib3

from storage.auxiliary.action_context_managers import ErrorSuppressionContextManager
from storage.auxiliary.numeration import number_to_hex_code
from storage.auxiliary.pwned.model import PWNED_PREFIX_CAPACITY

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PwnedRequester:
    """Pwned API client."""

    PWNED_RANGE_URL = "https://api.pwnedpasswords.com/range/"
    ATTEMPT_DELAYS = [0, 0, 30]
    DELAY_QUANTITY = len(ATTEMPT_DELAYS)

    def get_range(self, prefix_index: int) -> str:
        """
        Requests the Pwned password leak record range for an index of hash prefix.
        Performs retries if necessary.

        :param prefix_index: The index of the hash prefix to query.
        :return: The range as plain text.
        """
        hash_prefix = number_to_hex_code(prefix_index, PWNED_PREFIX_CAPACITY)
        for delay_index in range(self.DELAY_QUANTITY):
            self.__wait_for_delay(delay_index)
            if delay_index + 1 == len(self.ATTEMPT_DELAYS):
                with ErrorSuppressionContextManager():
                    return self.request_range(hash_prefix)
            else:
                return self.request_range(hash_prefix)

    def request_range(self, hash_prefix: str) -> str:
        """
        Requests the Pwned password leak record range for a hash prefix.

        :param hash_prefix: The hash prefix to query.
        :return: The range as plain text.
        """
        url = f"{self.PWNED_RANGE_URL}{hash_prefix}"
        response = requests.get(url, verify=False, timeout=30)
        response.raise_for_status()
        if not isinstance(response.text, str):
            raise ValueError("The text is expected to be string.")
        return response.text.replace("\r\n", "\n")

    def __wait_for_delay(self, delay_index) -> None:
        time.sleep(self.ATTEMPT_DELAYS[delay_index])
