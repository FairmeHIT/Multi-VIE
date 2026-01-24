import os
import json

def replace_json_type_values(folder_path):
    """
    Traverses all JSON files in the specified folder and its subfolders.
    Performs two modifications:
    1. Replaces 'type' values:
       - "ISO9000" -> "ISO9001"
       - "ISO14000" -> "ISO14001"
    2. Removes the "证书名称" (Certificate Name) field from the "result" dictionary.
    """
    # Traverse the folder and its subfolders
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check if the file is a JSON file
            if file.lower().endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    # Read the JSON file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Flag to check if any modifications were made
                    modified = False

                    # Check and replace 'type' value
                    if isinstance(data, dict) and 'type' in data:
                        if data['type'] == 'ISO9000':
                            data['type'] = 'ISO9001'
                            modified = True
                            print(f"Replaced 'ISO9000' with 'ISO9001' in {file_path}")
                        elif data['type'] == 'ISO14000':
                            data['type'] = 'ISO14001'
                            modified = True
                            print(f"Replaced 'ISO14000' with 'ISO14001' in {file_path}")

                    # Check and remove the "证书名称" field from "result"
                    if isinstance(data, dict) and 'result' in data and isinstance(data['result'], dict):
                        if '证书名称' in data['result']:
                            del data['result']['证书名称']
                            modified = True
                            print(f"Removed '证书名称' field from {file_path}")

                    # If modifications were made, write back to the file
                    if modified:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            # Preserve indentation
                            json.dump(data, f, ensure_ascii=False, indent=2)

                except json.JSONDecodeError:
                    print(f"Error: {file_path} is not a valid JSON file, skipped.")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    # Please replace this with your target folder path
    target_folder = "<TARGET_FOLDER_PATH>"

    # Check if the folder exists
    if not os.path.exists(target_folder):
        print(f"Error: Folder {target_folder} does not exist.")
    elif not os.path.isdir(target_folder):
        print(f"Error: {target_folder} is not a valid folder.")
    else:
        print(f"Starting to process folder: {target_folder}")
        replace_json_type_values(target_folder)
        print("Processing completed.")