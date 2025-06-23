# Ebook Organizer

A Python tool for organizing your ebook collection. It scans a source folder, extracts metadata (using local tools, Google Books API, or LLM), and sorts ebooks into a structured folder hierarchy by author and title. It also generates a CSV file with metadata for all processed ebooks.

## Features

- Supports EPUB, MOBI, AZW3, AZW, PDB, and PDF formats
- Extracts metadata from files, Google Books API, or LLM (Ollama)
- Organizes ebooks into folders by author and title
- Optionally writes metadata back to ebook files (except PDF)
- Generates a CSV summary of all processed ebooks
- Configurable via `config/config.yaml`
- Logging to file

## Requirements

- Python 3.8+
- [Calibre](https://calibre-ebook.com/) (for `ebook-meta` command)
- [Ollama](https://ollama.com/) (optional, for LLM metadata extraction)
- Python packages: see `requirements.txt` (e.g. `requests`, `pyyaml`)

## How to Run

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Install Calibre** and ensure `ebook-meta` is in your PATH.

3. *(Optional)* **Install Ollama** if you want to use LLM metadata extraction.

4. **Configure** the tool:
   - Edit `config/config.yaml` to set input/output folders and metadata keys.

5. **Place your ebooks** in the input folder (default: `unorganized_ebooks`).

6. **Run the script:**
   ```sh
   python main.py
   ```

7. **Check the output:**
   - Organized ebooks will be in the output folder (default: `organized_ebooks`)
   - Metadata summary in `ebooks.csv`
   - Logs in `organize_ebooks.log`

## Folder Structure

```
.
├── config/
│   └── config.yaml
├── logs/
│   └── organize_ebooks.log
├── metadata/
│   └── ... (metadata extraction scripts)
├── unorganized_ebooks/
│   └── ... (your source ebooks)
├── organized_ebooks/
│   └── ... (output, created by script)
├── utils/
│   └── ... (quality_check)
├── main.py
├── requirements.txt
└── README.md
```

## License

if you can use it, use it