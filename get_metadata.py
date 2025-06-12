import logging
from metadata.metadata_keys import metadata_keys
from metadata.get_metadata_ebook_meta import get_metadata_ebook_meta
from metadata.get_metadata_api import get_metadata_api
from metadata.get_metadata_llm import get_metadata_hard_llm, get_metadata_easy_llm, get_metadata_check_llm

ALL_METADATA_KEYS = metadata_keys()
FC = "get_metadata"

def build_query(file_path, metadata):
    query_parts = []
    for key in ALL_METADATA_KEYS:
        if key == "cover":
            continue
        value = metadata.get(key, "")
        if value:
            query_parts.append(f"{key}:{value}")
    if not query_parts:
        query_parts.append(file_path.stem)
    query = " ".join(query_parts)
    return query

def get_metadata(file_path, use_file_meta=False, use_file_meta_only=False, use_google_api=False, use_ollama=False, llm_model="llama3"):

    metadata = {key: "" for key in ALL_METADATA_KEYS}
    query = build_query(file_path, metadata)
    
    # 1. Get metadata from the file itself
    

    # Get metadata from the file itself only if all metadata is available
    if use_file_meta_only and all(metadata.get(key) for key in ALL_METADATA_KEYS):
        return metadata

    # Pokud je use_file_meta a máme všechna metadata, vrať je rovnou
    if use_file_meta and all(metadata.get(key) for key in ALL_METADATA_KEYS):
        logging.info(f"[{FC}] - DONE - All Metadata found in file for '{file_path}'")
        return metadata

    logging.info(f"[{FC}] - Metadata missing in file for '{file_path}', trying API/LLM")

    # 2. Get metadata from Google Books API
    if use_google_api and not all(metadata.get(key) for key in ALL_METADATA_KEYS):
        lang = metadata.get("language", None)
        api_metadata = get_metadata_api(query, lang) or {}
        for key in ALL_METADATA_KEYS:
            if not metadata.get(key) and api_metadata.get(key):
                metadata[key] = api_metadata[key]
        # Aktualizuj query po získání nových metadat
        query = build_query(file_path, metadata)

    # 3. Get metadata from the file_name using an 'LLM Easy'
    if use_ollama and not all(metadata.get(key) for key in ALL_METADATA_KEYS):
        llm_metadata = get_metadata_easy_llm(query, model=llm_model) or {}
        for key in ALL_METADATA_KEYS:
            if not metadata.get(key) and llm_metadata.get(key):
                metadata[key] = llm_metadata[key]
        # Update query after getting new metadata
        query = build_query(file_path, metadata)

    # If we still don't have all metadata, try to get it from the file itself
    if use_file_meta:
        file_metadata = get_metadata_ebook_meta(file_path)
        for key in ALL_METADATA_KEYS:
            if not metadata.get(key) and file_metadata.get(key):
                metadata[key] = file_metadata[key]
        query = build_query(file_path, metadata)

    # 4. Get metadata from first 3 pages using an 'LLM Hard'
    # if use_ollama and not all(metadata.get(key) for key in ALL_METADATA_KEYS):
    #     logging.info(f"[{FC}] - Querying 'LLM Hard' for '{query}'")
    #     llm_metadata = get_metadata_hard_llm(query, model=llm_model) or {}
    #     for key in ALL_METADATA_KEYS:
    #         if not metadata.get(key) and llm_metadata.get(key):
    #             metadata[key] = llm_metadata[key]

    # Double check metadata using the 'LLM Check'
    if use_ollama and not all(metadata.get(key) for key in ALL_METADATA_KEYS):
        logging.info(f"[{FC}] - Final 'LLM Check'")
        llm_metadata = get_metadata_check_llm(query, metadata, model=llm_model) or {}
        for key in ALL_METADATA_KEYS:
            if not metadata.get(key) and llm_metadata.get(key):
                metadata[key] = llm_metadata[key]

    logging.info(f"[{FC}] - Final metadata for '{file_path}':")
    logging.info(f"[{FC}] - '{metadata}'")
    return metadata