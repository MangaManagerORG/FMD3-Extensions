import os

from packaging import version
from packaging.version import Version


def bump_version(module_name, source_folder, level='patch'):
    v = parse_version(module_name, source_folder)
    level = "patch"  # Forcing it for now. Confused if it should be implemented this way or not.
    if v:
        if level == 'major':
            v = version.Version(f"{v.release[0] + 1}.0.0")
        elif level == 'minor':
            v = version.Version(f"{v.release[0]}.{v.release[1] + 1}.0")
        else:  # Default to bumping the patch version
            v = version.Version(f"{v.release[0]}.{v.release[1]}.{v.release[2] + 1}")

        # Save the bumped version back to __version__.py
        version_file_path = os.path.join(source_folder, module_name, "__version__.py")
        with open(version_file_path, 'w') as version_file:
            version_file.write(f"__version__ = '{v}'\n")

        print(f"Version bumped to {v}")


def parse_version(module_name, source_folder) -> Version:
    version_file_path = os.path.join(source_folder, module_name, "__version__.py")

    try:
        with open(version_file_path, 'r') as version_file:
            version_globals = {}
            exec(version_file.read(), version_globals)
            raw_version = version_globals.get('__version__')

            if raw_version:
                try:
                    # Validate the version using the packaging library
                    return version.parse(raw_version)
                except version.InvalidVersion:
                    print(f"Warning: Invalid version '{raw_version}' in '{module_name}'.")

            return None
    except FileNotFoundError:
        print(f"Warning: Version file not found for '{module_name}'.")
        return None
