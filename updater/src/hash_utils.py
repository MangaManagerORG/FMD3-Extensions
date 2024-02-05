import os
import subprocess

from .versioning import parse_version, bump_version


def get_latest_commit_hash(module_name, source_folder):
    try:
        git_command = f"git log -1 --pretty=format:%H -- {module_name}"
        result = subprocess.run(git_command, shell=True, cwd=source_folder, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def has_code_changed(module_id, module_name, source_folder, sources_data):
    latest_commit_hash = get_latest_commit_hash(module_name, source_folder)

    latest_hash = sources_data.get(module_name, {}).get('commit_hash')
    bump_type = os.getenv("BUMP_TYPE", "patch")
    if latest_hash and latest_hash == latest_commit_hash:
        return False
    else:
        bump_version(module_name, source_folder, bump_type)
        sources_data[module_id] = {
            "name": module_name,
            'commit_hash': latest_commit_hash,
            "version": parse_version(module_name, "src/sources").base_version
        }
        return True
