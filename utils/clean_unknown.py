import re

def clean_unkwown(value):
    """
    Cleans the input value by removing unwanted characters and formatting.
    Removes text in square brackets (e.g. "Jack London [London Jack]" -> "Jack London").
    :param value: The input string to clean.
    :return: A cleaned string, or an empty string if the input is unknown or empty
    """

    if not value or value.lower() in [
        "neznámý", "neznamy", "unknown", "unknown author",
        "www.online-convert.com", "0101", "ArtheWorld ۩ eKnihy",
        "5bdf262d2065261bea948f5e4d4d0dce", "stefamag", "9917"
    ]:
        return ""
    value = value.strip()
    # Remove text in square brackets and any surrounding whitespace
    value = re.sub(r'\s*\[.*?\]\s*', '', value).strip().strip('.')
    value = value.replace('_', '')
    return value

def clean_name(name):
    """
    Cleans the name by removing invalid characters and trimming whitespace.
    :param name: The name string to clean.
    :return: A cleaned name string with invalid characters removed.
    """
    
    return re.sub(r'[<>:"/\\|?*]', '', name).strip().rstrip('.')