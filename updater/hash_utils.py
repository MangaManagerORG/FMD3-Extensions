import os
import subprocess

from updater.CONSTANTS import SOURCES_PATH
from updater.versioning import parse_version, bump_version


def get_latest_commit_hash(module_name, source_folder):
    try:
        # get latest commit where the module was changed excluding the __version__.py file
        git_command = f'git log -1 --pretty=format:%H -- {SOURCES_PATH}/{module_name} ":^{SOURCES_PATH}/{module_name}/__version__.py"'
        result = subprocess.run(git_command, shell=True, capture_output=True, text=True, check=True)
        print(git_command)
        print(result_ := result.stdout.split("\n")[0].strip())
        return result_
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def has_code_changed(module_id, module_name, source_folder, sources_data):
    latest_commit_hash = get_latest_commit_hash(module_name, source_folder)

    latest_hash = sources_data.get(module_id, {}).get('commit_hash')
    bump_type = os.getenv("BUMP_TYPE", "patch")
    if latest_hash and latest_hash == latest_commit_hash:
        return False
    else:
        return True
