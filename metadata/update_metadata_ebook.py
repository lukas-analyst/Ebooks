import subprocess
import logging
import shutil
from metadata.metadata_keys import metadata_keys
from utils.clean_unknown import clean_name

ALL_METADATA_KEYS = metadata_keys()

def quote_arg(val):
    """
    Quotes the argument if it contains spaces or tabs.
    This is necessary for command line arguments to be parsed correctly.
    :param val: The value to be quoted.
    :return: The quoted value if it contains spaces or tabs, otherwise the value itself.
    """
    
    val = str(val)
    if " " in val or "\t" in val:
        return f'"{val}"'
    return val

def update_metadata_ebook(file_path, metadata):
    """
    Writes metadata to EPUB/MOBI/AZW3/AZW/PDB file using Calibre ebook-meta.
    Uses only relevant metadata for ebooks and technical file metadata.
    """

    ext = file_path.suffix
    file_dir = file_path.parent
    title = clean_name(metadata.get("title", "") or file_path.stem)
    new_filename = f"{title}{ext}"
    new_path = file_dir / new_filename

    # If the file already has the correct name, no need to rename
    if file_path != new_path:
        shutil.move(str(file_path), str(new_path))
        file_path = new_path

    args = ['ebook-meta', str(file_path)]
    
    # Add metadata arguments to the command
    if "author" in ALL_METADATA_KEYS and metadata.get("author"):
        args += ['--authors', quote_arg(metadata["author"])]
    if "title" in ALL_METADATA_KEYS and metadata.get("title"):
        args += ['--title', quote_arg(metadata["title"])]
    if "year" in ALL_METADATA_KEYS and metadata.get("year"):
        args += ['--date', quote_arg(metadata["year"])]
    if "isbn" in ALL_METADATA_KEYS and metadata.get("isbn"):
        args += ['--isbn', quote_arg(metadata["isbn"])]
    if "publisher" in ALL_METADATA_KEYS and metadata.get("publisher"):
        args += ['--publisher', quote_arg(metadata["publisher"])]
    if "language" in ALL_METADATA_KEYS and metadata.get("language"):
        args += ['--language', quote_arg(metadata["language"])]
    if "description" in ALL_METADATA_KEYS and metadata.get("description"):
        args += ['--comments', quote_arg(metadata["description"])]
    if "series" in ALL_METADATA_KEYS and metadata.get("series"):
        args += ['--series', quote_arg(metadata["series"])]
    if "series_index" in ALL_METADATA_KEYS and metadata.get("series_index"):
        args += ['--index', quote_arg(metadata["series_index"])]
    if "subjects" in ALL_METADATA_KEYS and metadata.get("subjects"):
        args += ['--tags', quote_arg(metadata["subjects"])]

    try:
        # subprocess.run(args, check=True) # Print output to console
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # Do not print output to console
    except Exception as e:
        logging.warning(f"update_metadata_ebook - Failed to set metadata for '{file_path}':")
        logging.warning(f"update_metadata_ebook - Error: {e}")