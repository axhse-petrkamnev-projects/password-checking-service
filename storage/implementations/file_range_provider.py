import asyncio

from storage.core.models.range_provider import PwnedRangeProvider


class FileRangeImporter(PwnedRangeProvider):
    """Imports ranges from a single data file."""

    def __init__(self, data_file_path: str):
        """
        Initialize a new FileRangeProvider instance.
        :param data_file_path: Path to the file where record data is stored.
        """
        self.__data_file_path: str = data_file_path

    async def get_range(self, prefix: str) -> str:
        """
        Gets the Pwned password leak record range from the data file.

        :param prefix: The hash prefix.
        :return: The range as plain text.
        """

        def find_offset(start, end):
            while start + 1 < end:
                mid = (start + end) // 2
                f.seek(mid)
                f.readline()  # Skip possibly partial line
                line = f.readline().decode("utf-8")
                if not line:
                    break  # EOF
                line_prefix = line[:5]
                if line_prefix < prefix:
                    start = mid
                else:
                    end = mid
            if start != 0:
                return end
            return start

        await asyncio.sleep(0)
        results = []
        with open(self.__data_file_path, "rb") as f:
            # Find start offset of the prefix
            start_offset = find_offset(0, f.seek(0, 2))

            # Read and process the lines between the found offsets
            f.seek(start_offset)
            if start_offset != 0:
                f.readline()
            while True:
                line = f.readline().decode("utf-8").strip()
                if not line or not line.startswith(prefix):
                    break
                results.append(line[5:])

        return "\n".join(results)
