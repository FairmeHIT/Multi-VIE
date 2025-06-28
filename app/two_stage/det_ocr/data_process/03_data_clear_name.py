import os
import re

def rename_txt_files(directory):
    # Regular expression pattern to match filenames
    pattern = re.compile(r'^(?P<base>[\w]{13})(?:[\w\s]*).txt$')

    # Traverse the specified directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for filename in files:
            match = pattern.match(filename)
            if match:
                base_name = match.group('base')  # Extract the "xx_xx_xxx_xxx" part

                # Construct the new filename
                new_filename = f"{base_name}.txt"

                # Get the full path of the file
                old_file_path = os.path.join(root, filename)
                new_file_path = os.path.join(root, new_filename)

                # Rename the file if the old filename is different from the new one
                if filename != new_filename:
                    os.rename(old_file_path, new_file_path)
                    print(f"Renamed {old_file_path} to {new_file_path}")
                else:
                    print(f"File {filename} is already in the standard format.")
            else:
                # The filename does not match the expected format
                print(f"File {filename} does not match the expected pattern and will not be renamed.")