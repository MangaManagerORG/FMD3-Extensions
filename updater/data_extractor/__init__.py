def get_extension_id(path,module_name):
    # Construct the module name dynamically
    file_path = f"{path}/{module_name}/{module_name}.py"

    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()

            # Search for the class definition using a regular expression
            import re
            class_pattern = re.compile(f"class\\s+{module_name}\\s*\\([^)]*\\):\\s*([^\\n]*)", re.DOTALL)
            match = class_pattern.search(file_contents)

            if match:
                class_definition = match.group(1)

                # Search for the ID attribute within the class definition
                id_pattern = re.compile(r"\bID\s*=\s*(['\"])(.*?)\1")
                id_match = id_pattern.search(class_definition)

                if id_match:
                    id_value = id_match.group(2)
                    return id_value
                else:
                    print(f"ID attribute not found in the class definition for {module_name}.")
            else:
                print(f"Class definition not found for {module_name}.")
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"Error while fetching ID for {module_name}: {e}")