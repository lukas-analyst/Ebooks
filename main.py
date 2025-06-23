import shutil
import csv
import logging
from pathlib import Path
from metadata.get_metadata import get_metadata
from metadata.update_metadata_ebook import update_metadata_ebook
from utils.clean_unknown import clean_name
from metadata.metadata_keys import metadata_keys
from config.load_config import load_config

CONFIG = load_config()
ALL_METADATA_KEYS = metadata_keys()

# Logging - get configuration from config.yaml (if true, logging_level, logging_file)
if CONFIG.get('logging', True):
    logging.basicConfig(
        level=CONFIG.get('logging_level', 'INFO').upper(),
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(CONFIG.get('logging_file', 'organize_ebooks.log'), encoding='utf-8'),
            # logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(level=logging.CRITICAL)

# Function to organize ebooks
def organize_ebooks():
    """
    Organizes ebooks from the source directory into an organized structure based on author and title.
    It scans the source directory for ebook files, retrieves their metadata, and organizes them into
    a structured folder hierarchy. It also writes a CSV file with the metadata of all processed ebooks.
    """

    src_dir = Path(CONFIG.get('input_folder', 'unorganized_ebooks'))
    dst = Path(CONFIG.get('output_folder', 'organized_ebooks'))
    books_info = []

    print(f"Scanning for ebooks in: {src_dir.resolve()}")
    all_files = [f for f in src_dir.rglob('*') if f.is_file()]
    print(f"Found {len(all_files)} files in the source directory.")

    if not src_dir.exists() or not all_files:
        logging.error(f"Source folder '{src_dir}' does not exist or is empty.")
        return

    # Scan the source directory for folders and files
    for idx, file in enumerate(all_files, 1):
        ext = file.suffix.lower()
        # Supported ebook formats
        if ext in ['.epub', '.mobi', '.azw3', '.azw', '.pdb', 'pdf']:
            print(f"Processing: {file.stem}")
            logging.info(f"Processing file: {file.stem}")
            metadata = get_metadata(
                file,
                use_file_meta=CONFIG.get('use_file_meta'),
                use_file_meta_only=CONFIG.get('use_file_meta_only'),
                use_google_api=CONFIG.get('google_api'),
                use_open_library_api=CONFIG.get('open_library_api'),
                use_llm=CONFIG.get('use_llm')
            )

            # Create the target directory structure
            if not dst.exists():
                dst.mkdir(parents=True, exist_ok=True)

            # If the author is empty, use "Unknown Author"
            author = clean_name(metadata.get("author", "") or "Unknown Author")
            # If the title is empty, use the file name without extension
            title = clean_name(metadata.get("title", "") or file.stem)

            # Create the target directory based on author and title
            target_dir = dst / author / title
            target_dir.mkdir(parents=True, exist_ok=True)
            new_filename = f"{title}{ext}"
            target_file = target_dir / new_filename

            print(f"Processed File N. {len(books_info) + 1} / {len(all_files)}:")
            print(f"{author} - {title}")

            # Copy the file to the target directory
            shutil.copy2(file, target_file)

            # Write the new metadata to the file (if allowed)
            if CONFIG.get('write_metadata') and ext not in ['.pdf']:
                update_metadata_ebook(target_file, metadata)

            # Write to CSV file
            books_info.append([v for k, v in metadata.items() if k != "cover" and v])
        
        else:
            logging.warning(f"Unsupported file format: {file.name} (skipping)")

    header = [k for k in ALL_METADATA_KEYS if k != "cover"]
    list_file = 'ebooks.csv'
    with open(list_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)
        writer.writerows(books_info)
    print("Done organizing ebooks.")

if __name__ == '__main__':
    organize_ebooks()