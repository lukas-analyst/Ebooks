# metadata/

This folder contains all scripts for retrieving, cleaning, and writing metadata for e-books.

## Contents

- **get_metadata.py** – main logic for retrieving metadata (combines various sources)
- **get_metadata_api.py** – retrieves metadata from the Google Books API
- **get_metadata_llm.py** – retrieves metadata using LLM (Ollama)
- **get_metadata_ebook_meta.py** – retrieves technical metadata from the file
- **open_ebook.py** – extracts text from various e-book formats
- **update_metadata_ebook.py** – writes metadata back to the e-book (via Calibre)
- **metadata_keys.py** – defines all used metadata keys
- **clean_unknown.py** – functions for cleaning and normalizing metadata values

## How to use

These scripts are intended to be used as part of the main program (`main.py`).  
You do not need to run them separately – they are called automatically as needed.