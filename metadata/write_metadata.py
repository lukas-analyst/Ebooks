import subprocess
import logging
import shutil
import re

def clean_name(name):
    return re.sub(r'[<>:"/\\|?*]', '', name).strip().rstrip('.')

def set_metadata_ebook_meta(file_path, metadata):
    """
    Zapíše metadata do EPUB/MOBI souboru pomocí Calibre ebook-meta.
    file_path: Path objekt k souboru
    metadata: dict se všemi klíči (viz ALL_METADATA_KEYS)
    """
    ext = file_path.suffix
    file_dir = file_path.parent
    title = clean_name(metadata.get("title", "") or file_path.stem)
    new_filename = f"{title}{ext}"
    new_path = file_dir / new_filename
    logging.info(f"Setting metadata for file: {file_path} -> {new_path}")
    logging.info(f"Metadata: {metadata}")

    # Pokud se název mění, přesuň soubor na nové místo
    if file_path != new_path:
        shutil.move(str(file_path), str(new_path))
        file_path = new_path

    args = ['ebook-meta', str(file_path)]
    if metadata.get("author"): args += ['--authors', metadata["author"]]
    if metadata.get("title"): args += ['--title', metadata["title"]]
    if metadata.get("year"): args += ['--date', metadata["year"]]
    if metadata.get("isbn"): args += ['--isbn', metadata["isbn"]]
    if metadata.get("publisher"): args += ['--publisher', metadata["publisher"]]
    if metadata.get("language"): args += ['--language', metadata["language"]]
    if metadata.get("description"): args += ['--comments', metadata["description"]]
    if metadata.get("series"): args += ['--series', metadata["series"]]
    if metadata.get("series_index"): args += ['--index', metadata["series_index"]]
    if metadata.get("subjects"): args += ['--tags', metadata["subjects"]]
    # Další pole lze přidat dle potřeby a možností ebook-meta

    logging.info(f"Setting metadata for '{file_path}': {args}")
    try:
        subprocess.run(args, check=True)
        logging.info(f"Metadata set successfully for '{file_path}'")
    except Exception as e:
        logging.warning(f"Failed to set metadata for '{file_path}': {e}")