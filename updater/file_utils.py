import json


def load_sources_data():
    sources_file_path = "extensions.json"  # Replace with the actual path to your centralized extensions.json
    try:
        with open(sources_file_path, 'r') as sources_file:
            return json.load(sources_file)
    except FileNotFoundError:
        return {}


def save_sources_data(data):
    sources_file_path = "extensions.json"  # Replace with the actual path to your centralized extensions.json
    with open(sources_file_path, 'w') as sources_file:
        json.dump(data, sources_file, indent=2)


