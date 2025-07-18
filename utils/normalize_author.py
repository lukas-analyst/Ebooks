from nameparser import HumanName

# Here you can add aliases for authors that might be commonly misnamed or have multiple variations.
# "wrong_name": "correct_name"
AUTHOR_ALIASES = {
    "Leo Tolstoj": "Lev Nikolajevič Tolstoj",
    "Leo Tolstoy": "Lev Nikolajevič Tolstoj",
    "Lev Tolstoj": "Lev Nikolajevič Tolstoj",
    "Lev Nikolajevic Tolstoj": "Lev Nikolajevič Tolstoj",
    "Lev Nikolajevic Tolstoy": "Lev Nikolajevič Tolstoj",
    "Čapek Karel": "Karel Čapek",
    "Hammingway Ernest": "Ernest Hemingway",
    "Pasternak Boris": "Boris Pasternak",
    "Verne Jules": "Jules Verne",
    "Fitzgerald F. Scott": "Francis Scott Fitzgerald",
    "Fitzgerald Francis Scott": "Francis Scott Fitzgerald",
    "Fitzgerald Scott": "Francis Scott Fitzgerald",
    "Wallace Edgar": "Edgar Wallace",
}

def normalize_author(author):
    name = HumanName(author)
    norm = f"{name.first} {name.last}".strip()
    return AUTHOR_ALIASES.get(norm, norm)