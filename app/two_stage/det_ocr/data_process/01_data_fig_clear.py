import os
import shutil
from PIL import Image  # Used to check if a file is an image (optional, but adds security)


def is_image_file(filename):
    """Check if the file is a supported image format"""
    IMG_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
    return any(filename.lower().endswith(ext) for ext in IMG_EXTENSIONS)


def move_images_to_folder(source_folder, destination_folder):
    """Move all images from source_folder and its subfolders to destination_folder"""
    # Create the destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Queue for folders to be traversed
    folders_to_search = [source_folder]

    while folders_to_search:
        # Get a folder from the queue
        current_folder = folders_to_search.pop(0)

        # Traverse all files and subfolders in the current folder
        for item in os.listdir(current_folder):
            # Build the full path
            item_path = os.path.join(current_folder, item)

            # If it's a folder, add it to the queue for later traversal
            if os.path.isdir(item_path):
                folders_to_search.append(item_path)
            # If it's an image file, move it to the destination folder
            elif is_image_file(item):
                # Build the destination path without the original subfolder structure, keeping only the filename
                # If you want to preserve the original subfolder structure, modify the code below
                # dest_path = os.path.join(destination_folder, os.path.relpath(item_path, source_folder))
                # Create the folder for the destination path if it doesn't exist
                # os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                # shutil.move(item_path, dest_path)

                # If not preserving subfolder structure, move images directly to the destination folder
                shutil.move(item_path, os.path.join(destination_folder, item))