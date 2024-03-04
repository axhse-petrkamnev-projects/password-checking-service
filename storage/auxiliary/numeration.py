def number_to_hex_code(number: int, capacity: int) -> str:
    """
    Convert a number to a hex string with fixed length based on specified hex value capacity.

    :param number: The number.
    :param capacity: The capacity.
    :return: A hex string.
    """
    if number < 0 or capacity <= number:
        raise ValueError("The number does not fit the capacity.")
    number_width = 0
    capacity -= 1
    while capacity > 0:
        number_width += 1
        capacity //= 16
    return hex(number)[2:].upper().rjust(number_width, "0")
