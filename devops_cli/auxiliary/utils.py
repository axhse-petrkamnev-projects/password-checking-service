import sys
from enum import Enum
from typing import List, Union


class TextStyle(Enum):
    """Console text style."""

    NONE = 0
    BOLD = 1
    ITALIC = 3
    BLACK = 30
    PALE_RED = 31
    PALE_GREEN = 32
    PALE_YELLOW = 33
    PALE_BLUE = 34
    PALE_PURPLE = 35
    PALE_CYAN = 36
    PALE_GRAY = 37
    GRAY = 90
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94
    PURPLE = 95
    CYAN = 96

    @property
    def pale(self):
        """
        Returns the pale version of the text style.
        :return: The pale version of the text style.
        """
        if self.value < TextStyle.RED.value or TextStyle.CYAN.value < self.value:
            return self
        return TextStyle(self.value - TextStyle.RED.value + TextStyle.PALE_RED.value)

    @property
    def bright(self):
        """
        Returns the bright version of the text style.
        :return: The bright version of the text style.
        """
        if (
            self.value < TextStyle.PALE_RED.value
            or TextStyle.PALE_CYAN.value < self.value
        ):
            return self
        return TextStyle(self.value - TextStyle.PALE_RED.value + TextStyle.RED.value)


def stylize_text(text: str, styles: Union[TextStyle, List[TextStyle]]) -> str:
    """
    Applies the specified text styles to the given text.

    :param text: The text to stylize.
    :param styles: A single style or a list of styles to apply.
    :return: The stylized text.
    """
    if isinstance(styles, TextStyle):
        styles = [styles]
    return "".join([f"\x1B[{style.value}m" for style in styles]) + text + "\x1B[0m"


def write(text: str) -> None:
    """
    Writes the provided text to the standard output.
    :param text: The text to write.
    """
    sys.stdout.write(text)
    sys.stdout.flush()


def convert_seconds(seconds: int) -> str:
    """
    Converts the amount of seconds to a formatted time string.

    :param seconds: The amount seconds to convert.
    :return: The formatted time string.
    """
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    seconds = seconds % 60
    hour_string = f"" if hours == 0 else "{hours}:"
    minute_string = f"{minutes:0{0 if hours == 0 else 2}d}"
    return f"{hour_string}{minute_string}:{seconds:02d}"
