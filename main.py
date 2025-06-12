import yaml
import re
import shutil
import csv
import logging
from pathlib import Path
from get_metadata import get_metadata
from metadata.write_metadata import set_metadata_ebook_meta


# Load configuration file
def load_config(config_path='config.yaml'):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

config = load_config()

# Logging - get configuration from config.yaml (if true, logging_level, logging_file)
if config.get('logging', True):
    logging.basicConfig(
        level=config.get('logging_level', 'INFO').upper(),
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(config.get('logging_file', 'organize_ebooks.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(level=logging.CRITICAL)

# Cleaning function to remove invalid characters from folder names
def clean_name(name):
    return re.sub(r'[<>:"/\\|?*]', '', name).strip().rstrip('.')

# Function to organize ebooks
def organize_ebooks():
    src_dir = Path(config.get('input_folder', 'unorganized_ebooks'))
    dst = Path(config.get('output_folder', 'organized_ebooks'))
    books_info = []

    logging.info(f"Scanning for ebooks in: {src_dir.resolve()}")

    # If the folder does not exists or is empty then log and exit
    if not src_dir.exists() or not any(src_dir.iterdir()):
        logging.error(f"Source folder '{src_dir}' does not exist or is empty.")
        return

    # Scan for all files in the source directory
    for file in src_dir.rglob('*'):
        if not file.is_file():
            continue

        logging.info(f"Processing file: {file}")
        metadata = get_metadata(
            file,
            use_file_meta=config.get('use_file_meta', False),
            use_file_meta_only=config.get('use_file_meta_only', False),
            use_google_api=config.get('google_api', False),
            use_ollama=config.get('ollama', False),
            llm_model=config.get('llm_model', 'llama3')
        )

        author = clean_name(metadata.get("author", "") or "Unknown Author")
        title = clean_name(metadata.get("title", "") or file.stem)

        target_dir = dst / author / title
        logging.info(f"Creating directory: {target_dir}")
        target_dir.mkdir(parents=True, exist_ok=True)

        ext = file.suffix
        new_filename = f"{title}{ext}"
        target_file = target_dir / new_filename
        shutil.copy2(file, target_file)

        if not dst.exists():
            logging.info(f"Creating output folder: {dst}")
            dst.mkdir(parents=True, exist_ok=True)

        # Write metadata to the file if required
        if config.get('write_metadata', False) and ext.lower() in ['.epub', '.mobi', '.azw3']:
            set_metadata_ebook_meta(target_file, metadata)

        # Add to list.txt
        books_info.append([v for k, v in metadata.items() if k != "cover" and v])


    list_file = 'ebooks.csv'
    logging.info(f"Writing final list to {list_file}")
    with open(list_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(books_info)
    logging.info("Done organizing ebooks.")

if __name__ == '__main__':
    organize_ebooks()