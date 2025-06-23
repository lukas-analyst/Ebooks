import logging
import ollama
from metadata.metadata_keys import metadata_keys
from utils.clean_unknown import clean_unkwown
from utils.is_valid_isbn import is_valid_isbn
from utils.normalize_author import normalize_author

ALL_METADATA_KEYS = metadata_keys()

SYSTEM_PROMPT = (
    "Your task is to extract only the (full name) author, title and the language of a book from the provided text. "
    "If you cannot determine the author or title, leave it empty. "
    "The language is meant to be the language in which the book is written."
    "The title should not include the author name."
    "Do not include any other information, comments or additional text. "
    "Usually the language is 'cs' or 'en'.\n"
    "Return only the metadata in the following format:\n"
    "Author: <author>\n"
    "Title: <title>\n"
    "Language: <language>\n"
    "ISBN: <isbn>\n\n"
)

def get_metadata_llm(file_path, probable_metadata=None):
    """
    Retrieves metadata for an ebook file using an LLM (Ollama).
    Response:
    Author: <author>
    Title: <title>
    Language: <language>
    :param file_path: Path to the ebook file.
    :return: A dictionary containing the metadata for the ebook.
    """

    try:
        # Create a prompt for the LLM
        probable_author = probable_metadata.get("author", "") if probable_metadata else ""
        probable_title = probable_metadata.get("title", "") if probable_metadata else ""
        prompt = f"{file_path}\n\n {probable_author} - {probable_title}"
        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        content = response["message"]["content"]
        logging.info(f"get_metadata_llm - LLM Response\n{content}")

        # Parse the response to extract metadata
        metadata_out = {key: "" for key in ALL_METADATA_KEYS}
        for line in content.splitlines():
            key, separator, value = line.partition(":")
            key = key.strip().lower()
            value = clean_unkwown(value.strip()) # Clean unwanted values
            if key == "isbn" and value and not is_valid_isbn(value): # Check if ISBN is valid
                value = ""
            if key == "author":
                value = normalize_author(value) # Normalize author name
            if key in metadata_out:
                metadata_out[key] = value
        return metadata_out

    except Exception as e:
        logging.warning("get_metadata_llm - Failed to check metadata with LLM")
        logging.warning(f"get_metadata_llm - Error: {e}")
        return {key: "" for key in ALL_METADATA_KEYS}