import os
import subprocess

def get_latest_commit_hash(module_path):
    """

    :param module_name:
    :param module_path: The path to the Module. ie: extensions/enrichers/<Module_name>
    :return:
    """
    try:
        # get latest commit where the module was changed excluding the __version__.py file
        git_command = f'git log -1 --pretty=format:%H -- {module_path} ":^{module_path}/__version__.py"'
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
    latest_commit_hash = get_latest_commit_hash(f"{source_folder}/{module_name}")

    latest_hash = sources_data.get(module_id, {}).get('commit_hash')
    bump_type = os.getenv("BUMP_TYPE", "patch")
    if latest_hash and latest_hash == latest_commit_hash:
        return False
    else:
        return True
