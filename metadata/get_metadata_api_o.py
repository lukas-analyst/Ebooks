
import requests
import logging
from metadata.metadata_keys import metadata_keys

ALL_METADATA_KEYS = metadata_keys()

def get_metadata_api_o(ebook_file_name, metadata=None):
    """
    Retrieves metadata from the Open Library API based on ebook_file_name or provided metadata.
    Tries multiple queries if nothing is found.
    :param ebook_file_name: The name of the ebook file (without extension).
    :param metadata: Optional dictionary containing metadata keys like 'isbn', 'author', 'title'.
    :return: A dictionary containing the metadata for the ebook.
    """

    base_url = "https://openlibrary.org"
    url= f"{base_url}/search.json"
    headers = {
        "User-Agent": "EbookOrganizer/0.1 (hanzliklukas2@gmail.com)"
    }
    params = {}
    queries = []

    if metadata and metadata.get("isbn"):
        queries.append(("isbn", metadata["isbn"]))
    if metadata and metadata.get("title"):
        queries.append(("title", metadata["title"]))
    queries.append(("filename", ebook_file_name))

    metadata_out = {key: "" for key in ALL_METADATA_KEYS}
    for query in queries:
        params["q"] = query
        logging.info(f"get_metadata_api_openlib - Looking for: {params['q']}")
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()
            docs = data.get("docs")
            if docs:
                book_data = docs[0]
                metadata_out.update({
                    "author": ", ".join(book_data.get("authors", [book_data.get("author_name", [""])[0]]) if "authors" in book_data else book_data.get("author_name", [])),
                    "title": book_data.get("title", ""),
                    "year": str(book_data.get("publish_date", book_data.get("first_publish_year", ""))),
                    "isbn": (book_data.get("isbn", [""])[0] if isinstance(book_data.get("isbn", []), list) else book_data.get("isbn", "")),
                    "publisher": (book_data.get("publishers", [""])[0] if isinstance(book_data.get("publishers", []), list) else book_data.get("publishers", "")),
                    "language": (book_data.get("languages", [{}])[0].get("key", "").replace("/languages/", "") if book_data.get("languages") else ""),
                    "description": book_data.get("description", "") if isinstance(book_data.get("description", ""), str) else book_data.get("description", {}).get("value", ""),
                    "subjects": ", ".join(book_data.get("subjects", [])),
                    "cover": f"https://covers.openlibrary.org/b/id/{book_data.get('cover_i')}-L.jpg" if book_data.get("cover_i") else "",
                    "identifiers": ", ".join(book_data.get("isbn", [])) if book_data.get("isbn") else "",
                    "page_count": str(book_data.get("number_of_pages", "")),
                })
                return metadata_out
            else:
                logging.info(f"get_metadata_api_openlib - No results for {query}")
        except Exception as e:
            logging.warning("get_metadata_api_openlib - Failed to get metadata from Open Library API")
            logging.warning(f"get_metadata_api_openlib - Error: {e}")
    return metadata_out

# Test
if __name__ == "__main__":
    # Example usage
    ebook_file_name = "example_book"
    metadata = {
        "isbn": "",
        "title": "Anna Kareninová 1",
        "author": "Lev Nikolajevič Tolstoj"
    }
    result = get_metadata_api_o(ebook_file_name, metadata)
    print(result)