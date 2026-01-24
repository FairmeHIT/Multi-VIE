import os
import chardet

def convert_to_utf8(input_dir):
    # Iterate through the specified directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            # Construct the full file path
            file_path = os.path.join(input_dir, filename)

            # Detect file encoding
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                encoding = chardet.detect(raw_data)['encoding']

            # Read file content using the detected encoding
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
            except UnicodeDecodeError:
                print(f"Failed to decode {file_path} with detected encoding: {encoding}.")
                continue

            # Save the content in UTF-8 encoding
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
                print(f"Converted {file_path} to UTF-8 encoding.")