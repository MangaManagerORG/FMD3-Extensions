import os
from pathlib import Path

from updater.CONSTANTS import SOURCES_PATH
from updater.utils import run_tests, zip_extension
from updater.file_utils import load_sources_data, save_sources_data
from updater.hash_utils import has_code_changed, get_latest_commit_hash
from updater.data_extractor import get_extension_id
from updater.versioning import bump_version, parse_version


def main():


    sources_data = load_sources_data()
    bumped = {}
    for generic_extension_path in filter(os.path.isdir, {dir for dir in Path("extensions").iterdir() if "__pycache__" not in str(dir)}):
        generic_extension = generic_extension_path.name
        bumped[generic_extension] = []
        print(f"scanning {generic_extension} extensions")
        extension_path = f"extensions/{generic_extension}"
        output_folder = Path(f"output/{generic_extension}")
        output_folder.mkdir(exist_ok=True,parents=True)

        if sources_data.get(generic_extension,None) is None:
            sources_data[generic_extension] = {}
        for module_path in filter(os.path.isdir, generic_extension_path.iterdir()):
            module_name = module_path.name
            module = f"extensions/{generic_extension}/{module_name}"
            if module_name == "__pycache__":
                continue
            # extensions/type/module_name
            module_id = get_extension_id(extension_path, module_name)
            assert module_id is not None
            if has_code_changed(module_id, module_name, extension_path, sources_data):
                print(f"Changes detected in extension '{module_name}'.")

                if run_tests(f"extensions/{generic_extension}",module_name):
                    bump_version(module)
                    sources_data[generic_extension][module_id] = {
                        "name": module_name,
                        'commit_hash': get_latest_commit_hash(module),
                        "version": parse_version(module).base_version
                    }

                    zip_extension(module_id, module_name, extension_path, output_folder)
                    bumped[generic_extension].append(module_name)
            else:
                print(f"No changes detected in extension '{module_name}'.")
    save_sources_data(sources_data)

    print("Bumped:")
    print(bumped)


if __name__ == "__main__":
    main()
