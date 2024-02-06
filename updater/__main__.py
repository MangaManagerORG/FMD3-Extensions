import os
from pathlib import Path

from updater.CONSTANTS import SOURCES_PATH
from updater.utils import run_tests, zip_extension
from updater.file_utils import load_sources_data, save_sources_data
from updater.hash_utils import has_code_changed, get_latest_commit_hash
from updater.data_extractor import get_extension_id
from updater.versioning import bump_version, parse_version

def main():
    output_folder = Path("output")
    output_folder.mkdir(exist_ok=True)  # Replace with the desired output path

    sources_data = load_sources_data()
    dirs = [d for d in os.listdir(SOURCES_PATH) if
            d != "__pycache__" and not d.startswith("sources") and not d.endswith(".py")]
    for module_name in dirs:
        module_id = get_extension_id(module_name)
        assert module_id is not None
        if has_code_changed(module_id, module_name, SOURCES_PATH, sources_data):
            print(f"Changes detected in extension '{module_name}'.")

            if run_tests(module_name):
                bump_version(module_name, SOURCES_PATH)
                sources_data[module_id] = {
                    "name": module_name,
                    'commit_hash': get_latest_commit_hash(module_name, SOURCES_PATH),
                    "version": parse_version(module_name, SOURCES_PATH).base_version
                }

                zip_extension(module_id, module_name, SOURCES_PATH, output_folder)
        else:
            print(f"No changes detected in extension '{module_name}'.")
    save_sources_data(sources_data)


if __name__ == "__main__":
    main()
