import unittest
import zipfile
import os


def run_tests(extension, module_name):
    tests_module = f"{extension}.{module_name}.tests"

    try:
        tests = unittest.defaultTestLoader.discover("extensions."+extension, pattern=f'test_{module_name}.py',
                                                    )
        result = unittest.TextTestRunner().run(tests)
        return result.wasSuccessful()
    except Exception as e:
        print(f"Error running tests for module {module_name}: {e}")


def zip_extension(module_id, module_name, source_folder, output_folder):
    extension_folder = os.path.join(source_folder, module_name)
    zip_filename = os.path.join(output_folder, f"{module_id}.zip")
    print(f"Zipping files to {zip_filename}")
    try:
        with zipfile.ZipFile(zip_filename, 'w') as zip_ref:
            for root, _, files in os.walk(extension_folder):
                for file in files:
                    file_path = os.path.join(root, file)

                    # Skip __pycache__ directories
                    if '__pycache__' in file_path:
                        continue
                    if 'tests' in file_path:
                        continue

                    arcname = os.path.relpath(file_path, source_folder)
                    print("Adding", f"{file_path:55}", " as ", arcname)
                    zip_ref.write(file_path, arcname)

        print(f"Extension '{module_name}' successfully zipped.")
    except Exception as e:
        print(f"Error zipping extension '{module_name}': {e}")

        print(f"Extension '{module_name}' successfully zipped.")
    except Exception as e:
        print(f"Error zipping extension '{module_name}': {e}")
