import os
from .src.utils import run_tests, zip_extension
from .src.file_utils import load_sources_data, save_sources_data
from .src.hash_utils import has_code_changed
from .src.data_extractor import get_extension_id


def main():
    src_folder = "src/sources"  # Replace with the actual path to your source extensions folder
    output_folder = "output"  # Replace with the desired output path

    sources_data = load_sources_data()
    dirs = [d for d in os.listdir(src_folder) if d != "__pycache__" and not d.startswith("sources") and not d.endswith(".py")]
    for module_name in dirs:
        module_id = get_extension_id(module_name)
        if has_code_changed(module_id,module_name, src_folder, sources_data):
            print(f"Changes detected in extension '{module_name}'.")
            if run_tests(module_name):
                zip_extension(module_id,module_name, src_folder, output_folder)

    save_sources_data(sources_data)

if __name__ == "__main__":
    main()