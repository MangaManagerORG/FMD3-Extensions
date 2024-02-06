import unittest
import zipfile
import os


def run_tests(module_name):
    try:
        tests_module = f"sources.{module_name}.tests"
        tests = unittest.defaultTestLoader.discover(tests_module, pattern=f'test_{module_name}.py',top_level_dir="src")
        result = unittest.TextTestRunner().run(tests)
        return result.wasSuccessful()
    except Exception as e:
        print(f"Error running tests for module '{module_name}': {e}")


def zip_extension(module_id,module_name, source_folder, output_folder):
    extension_folder = os.path.join(source_folder, module_name)
    zip_filename = os.path.join(output_folder, f"{module_id}.zip")

    try:
        with zipfile.ZipFile(zip_filename, 'w') as zip_ref:
            for root, _, files in os.walk(extension_folder):
                for file in files:
                    file_path = os.path.join(root, file)

                    # Skip __pycache__ directories
                    if '__pycache__' not in file_path:
                        arcname = os.path.relpath(file_path, source_folder)
                        print("Adding", file_path, "as", arcname)
                        zip_ref.write(file_path, arcname)

        print(f"Extension '{module_name}' successfully zipped.")
    except Exception as e:
        print(f"Error zipping extension '{module_name}': {e}")

        print(f"Extension '{module_name}' successfully zipped.")
    except Exception as e:
        print(f"Error zipping extension '{module_name}': {e}")