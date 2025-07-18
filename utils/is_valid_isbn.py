import re

def is_valid_isbn(isbn):
    """
    Checks if the given string is a valid ISBN-10 or ISBN-13.
    :param isbn: ISBN string (with or without hyphens/spaces)
    :return: True if valid, False otherwise
    """
    
    if not isbn:
        return False
    isbn = isbn.replace('-', '').replace(' ', '').upper()
    if len(isbn) == 10:
        # ISBN-10 validation
        if not re.match(r'^\d{9}[\dX]$', isbn):
            return False
        total = sum((10 - i) * (10 if x == 'X' else int(x)) for i, x in enumerate(isbn))
        return total % 11 == 0
    elif len(isbn) == 13:
        # ISBN-13 validation
        if not isbn.isdigit():
            return False
        total = sum((int(x) * (1 if i % 2 == 0 else 3)) for i, x in enumerate(isbn))
        return total % 10 == 0
    return False