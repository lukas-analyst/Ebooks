import logging
from metadata.metadata_keys import metadata_keys
from metadata.get_metadata_ebook_meta import get_metadata_ebook_meta
from metadata.get_metadata_api_g import get_metadata_api_g
from metadata.get_metadata_api_o import get_metadata_api_o
from metadata.get_metadata_llm import get_metadata_llm

ALL_METADATA_KEYS = metadata_keys()

def get_metadata(file_path, use_file_meta, use_file_meta_only, use_google_api, use_open_library_api, use_llm):
    """
    Retrieves metadata for an ebook file.
    This function attempts to extract metadata from the ebook file itself, then uses the Google Books API
    to fill in any missing information. If necessary, it can also use an LLM (Ollama) to suggest metadata based on the ebook's content.
    :param file_path: Path to the ebook file.
    :param use_file_meta: Whether to use metadata from the file itself.
    :param use_file_meta_only: If True, only return metadata if all keys are present in the file metadata.
    :param use_google_api: Whether to use the Google Books API to fill in missing metadata.
    :return: A dictionary containing the metadata for the ebook.
    """

    metadata = {key: "" for key in ALL_METADATA_KEYS}
    ebook_file_name = file_path.stem
    get_metadata_from_filesys_before = True
    
    # 1. Check if the file contains all metadata keys, if so, skip
    if use_file_meta_only:
        temp_metadata = get_metadata_ebook_meta(file_path)
        if all(temp_metadata.get(key) for key in ALL_METADATA_KEYS):
            logging.info("get_metadata - All metadata already present. Skipping")
            return metadata
    
    if use_file_meta and get_metadata_from_filesys_before:
        file_metadata = get_metadata_ebook_meta(file_path)
        logging.info(f"get_metadata_filesys - Metadata from the file itself: {file_metadata}")
        for key in ALL_METADATA_KEYS:
            if not metadata.get(key) and file_metadata.get(key):
                metadata[key] = file_metadata[key]

    # 2. Get metadata using the name of the file and feeding it LLM 
    if use_llm:
        if not metadata.get("author") or not metadata.get("title") or not metadata.get("language"):
            probable_metadata = {
                "author": metadata.get("author", ""),
                "title": metadata.get("title", ""),
                "language": metadata.get("language", ""),
                "isbn": metadata.get("isbn", "")
            }
        llm_metadata = get_metadata_llm(ebook_file_name, probable_metadata)
        logging.info(f"get_metadata_llm - Metadata from LLM: {llm_metadata}")
        for key in ALL_METADATA_KEYS:
            if llm_metadata.get(key):
                metadata[key] = llm_metadata[key]

    # 3. Get metadata from Open Library API using parameters from the LLM
    if use_open_library_api:
        open_library_metadata = get_metadata_api_o(ebook_file_name, metadata)
        logging.info(f"get_metadata_api_openlib - Metadata from Open Library API: {open_library_metadata}")
        for key in ALL_METADATA_KEYS:
            if open_library_metadata.get(key) and not metadata.get(key):
                metadata[key] = open_library_metadata[key]
    
    # 3. Get metadata from Google Books API using parameters from the LLM
    if use_google_api:
        google_metadata = get_metadata_api_g(ebook_file_name, metadata)
        logging.info(f"get_metadata_api_google - Metadata from Google Books API: {google_metadata}")  
        for key in ALL_METADATA_KEYS:
            if not metadata.get(key) and google_metadata.get(key):
                metadata[key] = google_metadata[key]

    return metadata