import yaml

# Load configuration file
def load_config(config_path='config\config.yaml'):
    """
    Load configuration from a YAML file.
    Returns a dictionary with the configuration settings.
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


    