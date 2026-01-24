import os
import sys
# Required library: send2trash, install with: pip install send2trash
from send2trash import send2trash

# Controls deletion mode for testing purposes
# True:  Simulate deletion (only show files to be deleted, no actual operation)
# False: Actually delete (move files to recycle bin)
SIMULATE_DELETION = False  # Change to False for actual deletion when testing is complete

def get_file_map(root_dir):
    """
    Scans the root directory and its subdirectories to create a file map.

    Args:
        root_dir (str): The root directory to scan.

    Returns:
        dict: A dictionary where keys are filenames without extensions,
              and values are lists of full file paths corresponding to each filename.
    """
    file_map = {}

    # Traverse the root directory and all its subdirectories
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            # Split filename and extension
            name_without_ext = os.path.splitext(filename)[0]
            file_path = os.path.join(dirpath, filename)

            # Add to the dictionary
            if name_without_ext not in file_map:
                file_map[name_without_ext] = []
            file_map[name_without_ext].append(file_path)

    return file_map

def find_mismatches(image_map, gt_map):
    """
    Finds mismatches between two file maps (e.g., images and their ground truths).

    Args:
        image_map (dict): File map for image files.
        gt_map (dict): File map for ground truth files.

    Returns:
        tuple: A tuple containing three lists:
              1. Files only present in the image map.
              2. Files only present in the ground truth map.
              3. Files where the count of images and ground truths do not match.
    """
    only_image = []
    only_gt = []
    count_mismatch = []

    # Check for files only present in images
    for name in image_map:
        if name not in gt_map:
            only_image.append((name, image_map[name]))

    # Check for files only present in ground truths
    for name in gt_map:
        if name not in image_map:
            only_gt.append((name, gt_map[name]))

    # Check for files with mismatched counts
    for name in image_map:
        if name in gt_map:
            if len(image_map[name]) != len(gt_map[name]):
                count_mismatch.append((
                    name,
                    len(image_map[name]),
                    image_map[name],
                    len(gt_map[name]),
                    gt_map[name]
                ))

    return only_image, only_gt, count_mismatch

def collect_files_to_delete(only_image, only_gt):
    """
    Collects all file paths that need to be deleted based on mismatches.

    Args:
        only_image (list): Files only present in the image directory.
        only_gt (list): Files only present in the ground truth directory.

    Returns:
        list: A list of full file paths to be deleted.
    """
    files_to_delete = []

    # Collect files only in image directory
    for _, paths in only_image:
        files_to_delete.extend(paths)

    # Collect files only in ground truth directory
    for _, paths in only_gt:
        files_to_delete.extend(paths)

    return files_to_delete

def delete_files(files_to_delete, simulate=SIMULATE_DELETION):
    """
    Deletes the specified files.

    Args:
        files_to_delete (list): List of full file paths to delete.
        simulate (bool): If True, only simulates deletion. If False, moves files to recycle bin.
    """
    if not files_to_delete:
        print("No files to delete.")
        return

    print(f"\n{'Simulating deletion of' if simulate else 'Deleting (moving to recycle bin) the following files:'}")
    for file_path in files_to_delete:
        print(f"- {file_path}")
        if not simulate:
            try:
                # Move file to recycle bin
                send2trash(file_path)
                print(f"  [OK] Moved to recycle bin.")
            except Exception as e:
                print(f"  [ERROR] Failed to move: {str(e)}")

def confirm_deletion(files_to_delete):
    """
    Asks the user for confirmation before proceeding with deletion.

    Args:
        files_to_delete (list): List of files to be deleted.

    Returns:
        bool: True if the user confirms deletion, False otherwise.
    """
    if not files_to_delete:
        return False

    print(f"\nFound {len(files_to_delete)} mismatched files to process.")
    response = input("Do you want to continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Operation cancelled.")
        return False

    # Display current deletion mode
    mode = "simulation" if SIMULATE_DELETION else "actual deletion (moving to recycle bin)"
    print(f"Current mode: {mode}")
    response = input(f"Proceed with {mode}? (y/n): ").strip().lower()
    return response == 'y'

def main():
    # Define the two root directories to check
    # TODO: Replace these placeholder paths with your actual directories
    IMAGE_DIR = "<IMAGE_DIRECTORY_PATH>"
    GT_DIR = "<GROUND_TRUTH_DIRECTORY_PATH>"

    # Validate directories
    if not os.path.isdir(IMAGE_DIR):
        print(f"Error: Directory '{IMAGE_DIR}' does not exist.")
        return

    if not os.path.isdir(GT_DIR):
        print(f"Error: Directory '{GT_DIR}' does not exist.")
        return

    # Get file maps
    print("Scanning files...")
    image_map = get_file_map(IMAGE_DIR)
    gt_map = get_file_map(GT_DIR)

    # Find mismatches
    only_image, only_gt, count_mismatch = find_mismatches(image_map, gt_map)

    # Output results
    print("\n===== Check Results =====")

    if not only_image and not only_gt and not count_mismatch:
        print("All files are properly paired. No mismatches found!")
        return

    if only_image:
        print(f"\nFiles only present in '{IMAGE_DIR}':")
        for name, paths in only_image:
            print(f"Filename: {name}")
            print(f"  Count: {len(paths)}")
            for path in paths:
                print(f"  - {path}")

    if only_gt:
        print(f"\nFiles only present in '{GT_DIR}':")
        for name, paths in only_gt:
            print(f"Filename: {name}")
            print(f"  Count: {len(paths)}")
            for path in paths:
                print(f"  - {path}")

    if count_mismatch:
        print(f"\nFiles with mismatched counts between directories:")
        for name, img_count, img_paths, gt_count, gt_paths in count_mismatch:
            print(f"Filename: {name}")
            print(f"  In '{IMAGE_DIR}': {img_count} file(s)")
            for path in img_paths:
                print(f"    - {path}")
            print(f"  In '{GT_DIR}': {gt_count} file(s)")
            for path in gt_paths:
                print(f"    - {path}")

    # Collect files to delete
    files_to_delete = collect_files_to_delete(only_image, only_gt)

    # If there are count mismatches, advise manual handling
    if count_mismatch and files_to_delete:
        print("\nWARNING: There are files with mismatched counts. It's recommended to handle these manually first.")
        response = input("Do you still want to delete files that exist in only one directory? (y/n): ").strip().lower()
        if response != 'y':
            print("Deletion operation cancelled.")
            return

    # Confirm and execute deletion
    if files_to_delete:
        if confirm_deletion(files_to_delete):
            delete_files(files_to_delete)

if __name__ == "__main__":
    main()