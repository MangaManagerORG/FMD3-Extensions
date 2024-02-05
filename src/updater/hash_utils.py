import subprocess

from updater.versioning import parse_version


def get_latest_commit_hash(module_name, source_folder):
    try:
        git_command = f"git log -1 --pretty=format:%H -- {module_name}"
        result = subprocess.run(git_command, shell=True, cwd=source_folder, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_latest_hash(module_name, sources_data):
    source_data = sources_data.get(module_name, {})
    return source_data.get('commit_hash')


def update_latest_hash(module_name, sources_data, commit_hash):
    sources_data[module_name] = {
        'commit_hash': commit_hash,
        "version": parse_version(module_name, "src/sources")
    }


def has_code_changed(module_name, source_folder, sources_data):
    latest_commit_hash = get_latest_commit_hash(module_name, source_folder)
    latest_hash = get_latest_hash(module_name, sources_data)

    if latest_hash and latest_hash == latest_commit_hash:
        return False
    else:
        update_latest_hash(module_name, sources_data, latest_commit_hash)
        return True
