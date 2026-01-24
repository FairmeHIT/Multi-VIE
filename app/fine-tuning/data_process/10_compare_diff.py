import json

def read_json_file(file_path):
    """
    Reads and parses a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict or list or None: Parsed JSON data if successful, None otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file")
        return None

def extract_addresses(json_data):
    """
    Extracts a list of file paths/addresses from JSON data.
    Supports both list and dictionary structures.

    Args:
        json_data (dict or list): The JSON data to extract addresses from.

    Returns:
        list: A list of extracted file path strings.
    """
    addresses = []
    if isinstance(json_data, list):
        # If JSON is a direct list of addresses (e.g., ["path1", "path2"])
        addresses = [str(item).strip() for item in json_data if item]
    elif isinstance(json_data, dict):
        # If JSON is a dictionary, attempt to extract strings from all values.
        # This logic can be modified based on the actual structure of your JSON.
        for key, value in json_data.items():
            if isinstance(value, str) and value.strip():
                addresses.append(value.strip())
            elif isinstance(value, list):
                # If the value is a list, recursively extract strings from it
                addresses.extend([str(item).strip() for item in value if isinstance(item, str) and item.strip()])
    else:
        print("Warning: Unsupported JSON data format (must be a list or dictionary)")
    return addresses

def compare_json_files(file1_path, file2_path):
    """
    Compares two JSON files containing file paths/addresses.
    It identifies common paths and paths unique to each file.

    Args:
        file1_path (str): Path to the first JSON file (e.g., from Windows).
        file2_path (str): Path to the second JSON file (e.g., from Linux).
    """
    # Read and parse JSON files
    data1 = read_json_file(file1_path)
    data2 = read_json_file(file2_path)

    if not data1 or not data2:
        return

    # Extract file addresses from both files
    addresses1 = extract_addresses(data1)
    addresses2 = extract_addresses(data2)

    # Convert to sets for easy comparison (ignores duplicates)
    set1 = set(addresses1)
    set2 = set(addresses2)

    # Calculate differences
    unique_to_file1 = set1 - set2  # Addresses only in file1
    unique_to_file2 = set2 - set1  # Addresses only in file2
    common_addresses = set1 & set2  # Addresses common to both files

    # Output results
    print(f"File '{file1_path}' contains {len(addresses1)} addresses (unique: {len(set1)})")
    print(f"File '{file2_path}' contains {len(addresses2)} addresses (unique: {len(set2)})")
    print(f"\nCommon addresses: {len(common_addresses)}")

    if unique_to_file1:
        print(f"\nAddresses unique to '{file1_path}' ({len(unique_to_file1)}):")
        for addr in sorted(unique_to_file1):
            print(f"  - {addr}")

    if unique_to_file2:
        print(f"\nAddresses unique to '{file2_path}' ({len(unique_to_file2)}):")
        for addr in sorted(unique_to_file2):
            print(f"  - {addr}")

if __name__ == "__main__":
    # Paths to the two JSON files to compare
    # These can be modified based on your actual file locations
    json_file_a = "files_list_win.json"
    json_file_b = "files_list_linux.json"

    compare_json_files(json_file_a, json_file_b)