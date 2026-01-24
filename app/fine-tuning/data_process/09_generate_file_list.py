import os
import json

def get_all_files_recursive(folder_path):
    """
    Recursively retrieves relative paths of all files in the specified folder and its subfolders.

    Args:
        folder_path (str): The root folder path to start scanning from.

    Returns:
        list: A list of relative file paths.

    Raises:
        ValueError: If the folder does not exist or the path is not a directory.
    """
    # Check if the folder exists
    if not os.path.exists(folder_path):
        raise ValueError(f"Folder does not exist: {folder_path}")

    if not os.path.isdir(folder_path):
        raise ValueError(f"Specified path is not a folder: {folder_path}")

    file_paths = []
    # Recursively traverse all subdirectories
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Get the relative path of the file with respect to the target folder
            relative_path = os.path.relpath(os.path.join(root, file), folder_path)
            file_paths.append(relative_path)

    return file_paths

def save_to_json(data, output_file="files_list.json"):
    """
    Saves data to a JSON file.

    Args:
        data (list): The list of file paths to be saved.
        output_file (str): The name of the output JSON file. Defaults to "files_list.json".
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved {len(data)} file paths to {output_file}")

if __name__ == "__main__":
    # Please replace this with the folder path you want to check
    target_folder = "<TARGET_FOLDER_PATH>"  # Can be replaced with an absolute path like "C:/my_files" or "/home/user/documents"

    try:
        # Get a list of relative paths for all files (including those in subfolders)
        file_list = get_all_files_recursive(target_folder)

        # Save to JSON file
        save_to_json(file_list)

    except Exception as e:
        print(f"An error occurred: {str(e)}")