import requests
import logging
from metadata.metadata_keys import metadata_keys

ALL_METADATA_KEYS = metadata_keys()

def get_metadata_api_g(ebook_file_name, metadata=None):
    """
    Retrieves metadata from the Google Books API based on a ebook_file_name or provided metadata.
    Tries multiple queries if nothing is found.
    :param ebook_file_name: The name of the ebook file (without extension).
    :param metadata: Optional dictionary containing metadata keys like 'isbn', 'author', 'title'.
    :return: A dictionary containing the metadata for the ebook.
    """

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"printType": "books"}
    queries = []

    if metadata and metadata.get("isbn"):
        queries.append(f"isbn:{metadata['isbn']}")
    if metadata and metadata.get("title") and metadata.get("author"):
        queries.append(f"intitle:{metadata['title']} inauthor:{metadata['author']}")
    if metadata and metadata.get("title"):
        queries.append(f"intitle:{metadata['title']}")
    queries.append(ebook_file_name)

    metadata_out = {key: "" for key in ALL_METADATA_KEYS}
    for query in queries:
        params["q"] = query
        logging.info(f"get_metadata_api_google - Looking for: {params['q']}")
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            items = data.get("items")
            if items:
                info = items[0].get("volumeInfo", {})
                industry_ids = info.get("industryIdentifiers", [])
                metadata_out.update({
                    "author": ", ".join(info.get("authors", [])),
                    "title": info.get("title", params["q"]),
                    "year": str(info.get("publishedDate", ""))[:4],
                    "isbn": next((i["identifier"] for i in industry_ids if i["type"] == "ISBN_13"), ""),
                    "publisher": info.get("publisher", ""),
                    "language": info.get("language", ""),
                    "description": info.get("description", ""),
                    "subjects": ", ".join(info.get("categories", [])),
                    "cover": info.get("imageLinks", {}).get("thumbnail", ""),
                    "identifiers": ", ".join([f"{i['type']}:{i['identifier']}" for i in industry_ids]),
                    "page_count": str(info.get("pageCount", "")),
                })
                return metadata_out
            else:
                logging.info(f"get_metadata_api_google - No results for '{query}'")
        except Exception as e:
            logging.warning("get_metadata_api_google - Failed to get metadata from Google Books API")
            logging.warning(f"get_metadata_api_google - Error: {e}")
    return metadata_out