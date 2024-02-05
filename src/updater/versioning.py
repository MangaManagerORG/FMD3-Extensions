import os

from packaging import version


def bump_version(module_name, source_folder, level='patch'):
    v = parse_version(module_name, source_folder)

    if v:
        if level == 'major':
            v = v.next_major()
        elif level == 'minor':
            v = v.next_minor()
        else:  # Default to bumping the patch version
            v = v.next_patch()

        # Save the bumped version back to __version__.py
        version_file_path = os.path.join(source_folder, module_name, "__version__.py")
        with open(version_file_path, 'w') as version_file:
            version_file.write(f"__version__ = '{v}'\n")

        print(f"Version bumped to {v}")


def parse_version(module_name, source_folder):
    version_file_path = os.path.join(source_folder, module_name, "__version__.py")

    try:
        with open(version_file_path, 'r') as version_file:
            version_globals = {}
            exec(version_file.read(), version_globals)
            raw_version = version_globals.get('__version__')

            if raw_version:
                try:
                    # Validate the version using the packaging library
                    version_obj = version.parse(raw_version)
                    return raw_version
                except version.InvalidVersion:
                    print(f"Warning: Invalid version '{raw_version}' in '{module_name}'.")

            return None
    except FileNotFoundError:
        print(f"Warning: Version file not found for '{module_name}'.")
        return None
