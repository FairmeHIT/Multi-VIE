import os

def get_image_extensions():
    """Return common image file extensions."""
    return {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

def collect_image_names(folder):
    """
    Collect filenames of all images (without paths) in the specified folder and its subfolders.

    Args:
        folder (str): Path to the folder to traverse.

    Returns:
        set: A set containing all image filenames.
    """
    image_extensions = get_image_extensions()
    image_names = set()

    if not os.path.isdir(folder):
        print(f"Warning: Folder '{folder}' does not exist or is not a valid directory.")
        return image_names

    for root, _, files in os.walk(folder):
        for file in files:
            # Check if the file extension is an image format
            _, ext = os.path.splitext(file.lower())
            if ext in image_extensions:
                image_names.add(file.lower())  # Convert to lowercase for case-insensitive comparison

    return image_names

def remove_duplicate_images(source_folder, target_folder, dry_run=False):
    """
    Remove images in the target folder that have the same name as images in the source folder.

    Args:
        source_folder (str): Path to the source folder.
        target_folder (str): Path to the target folder.
        dry_run (bool): If True, only display files to be deleted without actually deleting them.
    """
    # Collect all image filenames from the source folder
    source_image_names = collect_image_names(source_folder)
    print(f"Found {len(source_image_names)} image files in source folder '{source_folder}'.")

    if not source_image_names:
        print("No image files found in the source folder. No deletion needed.")
        return

    image_extensions = get_image_extensions()
    deleted_count = 0

    # Traverse the target folder and delete duplicate images
    for root, _, files in os.walk(target_folder):
        for file in files:
            # Check if the file extension is an image format
            _, ext = os.path.splitext(file.lower())
            if ext in image_extensions:
                # Check if the filename exists in the source folder
                if file.lower() in source_image_names:
                    file_path = os.path.join(root, file)
                    if dry_run:
                        print(f"Would delete: {file_path}")
                        deleted_count += 1
                    else:
                        try:
                            os.remove(file_path)
                            print(f"Deleted: {file_path}")
                            deleted_count += 1
                        except Exception as e:
                            print(f"Error deleting file '{file_path}': {e}")

    if dry_run:
        print(f"\nDry run completed. Found {deleted_count} files to delete.")
    else:
        print(f"\nOperation completed. Deleted {deleted_count} files.")

if __name__ == "__main__":
    # Specify source and target folder paths here
    source_folder = "<SOURCE_FOLDER_PATH>"  # Replace with your source folder path
    target_folder = "<TARGET_FOLDER_PATH>"  # Replace with your target folder path
    dry_run = False  # Set to True for testing without actual deletion; set to False to perform deletion

    # Check if source and target folders exist
    if not os.path.isdir(source_folder):
        print(f"Error: Source folder '{source_folder}' does not exist or is not a valid directory.")
    elif not os.path.isdir(target_folder):
        print(f"Error: Target folder '{target_folder}' does not exist or is not a valid directory.")
    else:
        # Execute the deletion operation
        remove_duplicate_images(source_folder, target_folder, dry_run)