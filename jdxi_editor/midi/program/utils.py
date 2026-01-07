def get_previous_program_bank_and_number(
    program_number: int, bank_letter: str
) -> tuple[str, int]:
    """
    get previous program bank number

    :param program_number: int
    :param bank_letter: str
    :return: tuple[str,int]
    """
    if program_number > 1:
        program_number -= 1
    elif bank_letter == "A":
        program_number = 64  # wrap around to 64
        bank_letter = "H"
    else:
        program_number = 64  # wrap around to 64
        bank_letter = chr(ord(bank_letter) - 1)
    return bank_letter, program_number


def get_next_program_bank_and_number(
    program_number: int, bank_letter: str
) -> tuple[int, str]:
    """
    get next program bank number

    :param program_number: int
    :param bank_letter: str
    :return: tuple
    """
    if program_number < 64:
        program_number += 1
    elif bank_letter == "H":
        program_number = 1  # reset program number, wrap around to 1
        bank_letter = "A"  # reset bank letter
    else:
        program_number = 1  # reset program number
        bank_letter = chr(ord(bank_letter) + 1)
    return program_number, bank_letter
