import subprocess
import logging
import re
from metadata.metadata_keys import metadata_keys
from utils.clean_unknown import clean_unkwown
from utils.is_valid_isbn import is_valid_isbn

ALL_METADATA_KEYS = metadata_keys()

def get_metadata_ebook_meta(file_path):
    """
    Retrieves metadata from an ebook file using the `ebook-meta` command-line tool.
    :param file_path: Path to the ebook file.
    :return: A dictionary containing the metadata for the ebook.
    """
    metadata = {key: "" for key in ALL_METADATA_KEYS}

    try:
        result = subprocess.run(
            ['ebook-meta', str(file_path)],
            capture_output=True, text=True, check=True, encoding='utf-8'
        )
        output = result.stdout

        regex_map = {
            "author": r'Author\(s\)\s*:\s*(.+)',
            "title": r'Title\s*:\s*(.+)',
            "year": r'Published\s*:\s*(\d{4})',
            "isbn": r'Identifiers\s*:\s*isbn:(\d+)',
            "publisher": r'Publisher\s*:\s*(.+)',
            "language": r'Language\s*:\s*(.+)',
            "description": r'Description\s*:\s*(.+)',
            "series": r'Series\s*:\s*(.+)',
            "series_index": r'Series index\s*:\s*(.+)',
            "subjects": r'Tags\s*:\s*(.+)',
            "cover": r'Cover\s*:\s*(.+)',
            "identifiers": r'Identifiers\s*:\s*(.+)',
            "contributors": r'Contributors\s*:\s*(.+)',
            "rights": r'Rights\s*:\s*(.+)',
            "format": r'Format\s*:\s*(.+)',
            "source": r'Source\s*:\s*(.+)',
            "modification_date": r'Modified\s*:\s*(.+)',
            "creation_date": r'Created\s*:\s*(.+)',
            "page_count": r'Page count\s*:\s*(\d+)',
            "file_size": r'File size\s*:\s*(.+)',
        }

        for key in ALL_METADATA_KEYS:
            if key in regex_map:
                match = re.search(regex_map[key], output)
                value = clean_unkwown(match.group(1)) if match else ""
                # Kontrola ISBN
                if key == "isbn" and value and not is_valid_isbn(value):
                    value = ""
                metadata[key] = value

        # Remove empty metadata fields
        metadata = {k: v for k, v in metadata.items() if v}
        return metadata
    except Exception as e:
        logging.warning(f"get_metadata_ebook_meta - Failed to get metadata from ebook-meta for '{file_path}'")
        logging.warning(f"get_metadata_ebook_meta - Error: {e}")
        return {key: "" for key in ALL_METADATA_KEYS}