import subprocess
import logging
import re
import os
from metadata.metadata_keys import metadata_keys

ALL_METADATA_KEYS = metadata_keys()
FC = "get_metadata_ebook_meta"

def get_metadata_ebook_meta(file_path):
    metadata = {key: "" for key in ALL_METADATA_KEYS}
    try:
        # File format check
        if not str(file_path).lower().endswith(('.epub', '.mobi', '.azw3')):
            logging.info(f"[{FC}] - File format not supported {file_path}")
            return metadata

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

        def clean(val):
            if not val:
                return ""
            val = val.strip()
            if val.lower() in ["neznámý", "neznamy", "unknown"]:
                return ""
            return val

        for key in ALL_METADATA_KEYS:
            if key in regex_map:
                match = re.search(regex_map[key], output)
                metadata[key] = clean(match.group(1)) if match else ""

        # Remove empty metadata fields
        metadata = {k: v for k, v in metadata.items() if v}

        logging.info(f"[{FC}] - ebook-meta for '{file_path}': {metadata}")
        return metadata
    except Exception as e:
        logging.warning(f"[{FC}] - Failed to get metadata from ebook-meta for '{file_path}': {e}")
        return {key: "" for key in ALL_METADATA_KEYS}