import os
import shutil

def move_txt_files(src_dir, dest_dir):
    # Iterate through all files and subdirectories under src_dir
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            # Check if it is a .txt file
            if file.endswith('.txt'):
                # Construct the full source file path
                src_file_path = os.path.join(root, file)
                # Construct the destination file path
                dest_file_path = os.path.join(dest_dir, file)

                # Move the file
                shutil.move(src_file_path, dest_file_path)
                print(f"Moved {src_file_path} to {dest_file_path}")