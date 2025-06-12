import requests
import logging
from metadata.metadata_keys import metadata_keys

ALL_METADATA_KEYS = metadata_keys()
FC = "get_metadata_api"

def get_metadata_api(query, lang=None, metadata=None):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {}

    # If metadata is provided, use it to build the query with params
    if metadata:
        if metadata.get("isbn"):
            params["q"] = f"isbn:{metadata['isbn']}"
        elif metadata.get("author") and metadata.get("title"):
            params["q"] = f"intitle:{metadata['title']}+inauthor:{metadata['author']}"
        elif metadata.get("title"):
            logging.info(f"[{FC}] - API looking for '{metadata.get("title")}'")
            params["q"] = f"intitle:{metadata['title']}"
        else:
            params["q"] = query
    else:
        logging.info(f"[{FC}] - API looking for '{query}'")
        params["q"] = query

    if lang:
        params["langRestrict"] = lang
    params["printType"] = "books"
    metadata_out = {key: "" for key in ALL_METADATA_KEYS}
    try:
        logging.info(f"[{FC}] - Google Books API complete request: {url, params}")
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if "items" in data:
            info = data["items"][0]["volumeInfo"]
            metadata_out["author"] = ", ".join(info.get("authors", []))
            metadata_out["title"] = info.get("title", params["q"])
            metadata_out["year"] = info.get("publishedDate", "")[:4]
            metadata_out["isbn"] = ""
            for id in info.get("industryIdentifiers", []):
                if id["type"] == "ISBN_13":
                    metadata_out["isbn"] = id["identifier"]
            metadata_out["publisher"] = info.get("publisher", "")
            metadata_out["language"] = info.get("language", "")
            metadata_out["description"] = info.get("description", "")
            metadata_out["subjects"] = ", ".join(info.get("categories", []))
            metadata_out["cover"] = info.get("imageLinks", {}).get("thumbnail", "")
            metadata_out["identifiers"] = ", ".join([f"{i['type']}:{i['identifier']}" for i in info.get("industryIdentifiers", [])])
            logging.info(f"[{FC}] - {metadata_out}")
            return metadata_out
        else:
            logging.info(f"[{FC}] - No items found in Google Books API for '{params['q']}'")
    except Exception as e:
        logging.warning(f"[{FC}] - Failed to get metadata from Google Books for '{params['q']}': {e}")
    return metadata_out