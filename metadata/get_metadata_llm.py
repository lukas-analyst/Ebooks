import logging
import ollama
import yaml
import os
import re
from metadata.metadata_keys import metadata_keys

ALL_METADATA_KEYS = metadata_keys()
FC = "get_metadata_llm"

def get_metadata_easy_llm(query, model="llama3"):
    metadata = {key: "" for key in ALL_METADATA_KEYS}
    try:
        prompt = (
            f"From the filename '{query}', estimate the title, author (full name), year of publication, and ISBN of the book. "
            "It is important that the name is in the format 'surname first_name' (e.g., 'Orwell George', or 'Pasternak Boris'). "
            "Return the result separated by a vertical bar (|) in the format: "
            "author(s) | title | year | ISBN | language "
            "If you do not know some values (such as ISBN), leave them blank. Do not make them up. "
            "Respond so that the output is easy to process. Be precise like a robot, do not add parentheses unless necessary. "
            "No additional comments or explanations, only clean text output. Respond in the language of the book (if available, otherwise in English)."
        )
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response["message"]["content"].strip()

        parts = [p.strip() for p in content.split("|")]
        while len(parts) < 4:
            parts.append("")
        metadata["author"], metadata["title"], metadata["year"], metadata["isbn"] = parts[:4]

        for k in metadata:
            if isinstance(metadata[k], str):
                metadata[k] = metadata[k].replace('\n', ' ').replace('\r', ' ').strip()
        logging.info(f"[{FC}] - LLM Easy metadata for '{query}':")
        logging.info(f"[{FC}] - {metadata}")
        return metadata
    except Exception as e:
        logging.warning(f"[{FC}] - Failed to get metadata from LLM for '{query}': {e}")
        return metadata

def get_metadata_hard_llm(query, book, model="llama3"):
    logging.info(f"[{FC}] - Querying LLM Hard for '{query}'")
    metadata = {key: "" for key in ALL_METADATA_KEYS}
    try:
        prompt = (
            f"Z těchto prvních 3 stran knihy '{query}':\n\n{book}\n\n"
            "Odhadni co nejvíce metadatových polí. Výsledek vrať ve formátu YAML se všemi běžnými klíči: "
            "author, title, year, isbn, publisher, language, description, series, series_index, subjects, cover, identifiers, contributors, rights, format, source, modification_date, creation_date, page_count, file_size. "
            "Pokud některé hodnoty neznáš, nech je prázdné. Odpověz tak, aby výstup šel snadno zpracovat. Buď přesný jako robot, nepřidávej závorky, pokud nejsou nutné. Žádné další komentáře ani vysvětlení, pouze čistý YAML výstup. Odpověz v češtině."
        )
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response["message"]["content"].strip()
        try:
            llm_data = yaml.safe_load(content)
            if isinstance(llm_data, dict):
                for key in ALL_METADATA_KEYS:
                    if key in llm_data and llm_data[key] is not None:
                        metadata[key] = str(llm_data[key])
        except Exception as e:
            logging.warning(f"[{FC}] - YAML parsing failed for '{query}': {e}")
        for k in metadata:
            if isinstance(metadata[k], str):
                metadata[k] = metadata[k].replace('\n', ' ').replace('\r', ' ').strip()
        logging.info(f"[{FC}] - LLM Hard metadata for '{query}': {metadata}")
        return metadata
    except Exception as e:
        logging.warning(f"[{FC}] - Failed to get metadata from LLM for '{query}': {e}")
        return metadata

def strip_markdown_blocks(text):
    return re.sub(r"^```[a-zA-Z]*\s*|```$", "", text, flags=re.MULTILINE).strip()

def get_metadata_check_llm(query, metadata, model="llama3"):
    logging.info(f"[{FC}] - Checking metadata with LLM for '{query}'")
    try:
        prompt = (
            f"Check the following metadata for the book '{query}':\n\n"
            f"{yaml.dump(metadata)}\n\n"
            "Reply in YAML format with the keys 'valid' (boolean) and 'message' (string)."
            "An empty value is not a problem, but the metadata must be valid and meaningful. Diacritics in the title are correct. "
            "The metadata must also contain 'title' and 'author'."
            "If the metadata is valid, return valid: true and an empty message. "
            "If it is invalid, return valid: false and a message describing the problem. "
        )
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response["message"]["content"].strip()
        content = strip_markdown_blocks(content)
        check_result = yaml.safe_load(content)
        if isinstance(check_result, dict) and 'valid' in check_result:
            if not check_result.get("valid", False):
                # Pokud jsou metadata neplatná, ulož YAML s názvem podle title a přidej i výsledek kontroly
                title = metadata.get("title", "chyba_metadata").strip() or "chyba_metadata"
                safe_title = "".join(c for c in title if c.isalnum() or c in " _-").rstrip()
                os.makedirs("problems", exist_ok=True)
                filename = os.path.join("problems", f"{safe_title}.yaml")
                with open(filename, "w", encoding="utf-8") as f:
                    yaml.dump({
                        "metadata": metadata,
                        "llm_check_result": check_result
                    }, f, allow_unicode=True)
                logging.warning(f"[{FC}] - Invalid metadata saved to {filename}")
            return check_result
        else:
            # Ulož i případ, kdy je odpověď od LLM neplatná
            title = metadata.get("title", "chyba_metadata").strip() or "chyba_metadata"
            safe_title = "".join(c for c in title if c.isalnum() or c in " _-").rstrip()
            os.makedirs("problems", exist_ok=True)
            filename = os.path.join("problems", f"{safe_title}_chyba.yaml")
            with open(filename, "w", encoding="utf-8") as f:
                yaml.dump({
                    "metadata": metadata,
                    "llm_response": content,
                    "error": "Neplatný formát odpovědi od LLM"
                }, f, allow_unicode=True)
            logging.warning(f"[{FC}] - Invalid response format from LLM for '{query}': {content}")
            return {"valid": False, "message": "Neplatný formát odpovědi od LLM"}
    except Exception as e:
        # Ulož i případnou výjimku
        title = metadata.get("title", "chyba_metadata").strip() or "chyba_metadata"
        safe_title = "".join(c for c in title if c.isalnum() or c in " _-").rstrip()
        os.makedirs("problems", exist_ok=True)
        filename = os.path.join("problems", f"{safe_title}_exception.yaml")
        with open(filename, "w", encoding="utf-8") as f:
            yaml.dump({
                "metadata": metadata,
                "error": str(e)
            }, f, allow_unicode=True)
        logging.warning(f"[{FC}] - Failed to check metadata with LLM for '{query}': {e}")
        return {"valid": False, "message": str(e)}