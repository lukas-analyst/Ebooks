import yaml
from pathlib import Path

def metadata_keys(config_path=Path("config\config.yaml")):
    
    """
    Load metadata keys from the configuration file.
    Returns a list of metadata keys that are set to True in the configuration.
    If the configuration is not a dictionary, it returns the list directly.
    """

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    keys = config.get("ALL_METADATA_KEYS", {})
    if isinstance(keys, dict):
        return [k for k, v in keys.items() if v is True]
    return list(keys)