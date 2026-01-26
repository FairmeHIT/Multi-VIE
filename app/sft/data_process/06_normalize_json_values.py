import os
import json


def process_json_files(root_dir):
    """
    Traverses all JSON files in the root directory and its subdirectories.
    Performs two modifications on the 'result' field (if it exists and is a dictionary):
    1. Replaces string values of "unidentified" or "未识别到" with Python's None (null in JSON).
    2. Replaces string values of "True" or "False" with their corresponding boolean values.

    Args:
        root_dir (str): The root directory to start processing from.
    """
    # Strings that should be replaced with None (null)
    null_targets = {"unidentified", "未识别到"}
    # Strings that should be replaced with boolean values
    bool_targets = {"True", "False"}

    # Traverse the directory
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            # Check if the file is a JSON file
            if filename.lower().endswith('.json'):
                file_path = os.path.join(dirpath, filename)
                try:
                    # Read the JSON file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Check if 'result' field exists and is a dictionary
                    if 'result' in data and isinstance(data['result'], dict):
                        modified = False
                        # Iterate over all key-value pairs in 'result'
                        for key, value in data['result'].items():
                            # Check if value is a string that needs to be replaced with None
                            if isinstance(value, str) and value in null_targets:
                                data['result'][key] = None
                                modified = True
                            # Check if value is a string that needs to be replaced with a boolean
                            elif isinstance(value, str) and value in bool_targets:
                                data['result'][key] = True if value == "True" else False
                                modified = True

                        # If any modifications were made, save the file
                        if modified:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                # Preserve indentation
                                json.dump(data, f, ensure_ascii=False, indent=2)
                            print(f"Updated: {file_path}")
                    else:
                        print(f"Skipped (no valid 'result' field): {file_path}")

                except json.JSONDecodeError:
                    print(f"Error: Could not parse JSON file {file_path}")
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")


if __name__ == "__main__":
    # Replace with your target folder path
    target_directory = "<TARGET_DIRECTORY_PATH>"

    # Validate the directory exists
    if not os.path.isdir(target_directory):
        print(f"Error: Directory '{target_directory}' does not exist")
    else:
        print(f"Starting to process directory: {target_directory}")
        process_json_files(target_directory)
        print("Processing completed.")