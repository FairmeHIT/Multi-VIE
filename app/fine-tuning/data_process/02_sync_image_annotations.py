import os
import shutil
from os.path import splitext
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define source and target folder paths
# TODO: Replace placeholders with actual paths before running
IMAGE_SOURCE = "<IMAGE_SOURCE_FOLDER>"  # Source folder for images
GT_SOURCE = "<GT_SOURCE_FOLDER>"  # Source folder for ground truth annotations
IMAGE_OK = "<IMAGE_TARGET_FOLDER>"  # Target folder for processed images
GT_OK = "<GT_TARGET_FOLDER>"  # Target folder for processed annotations

# Define list of subfolders to exclude
EXCLUDE_FOLDERS = ["VIE_result", "xuexinnet", "classify_failed", "classify_result"]

# Ensure target folders exist
os.makedirs(IMAGE_OK, exist_ok=True)
os.makedirs(GT_OK, exist_ok=True)


def process_file(file_info):
    """
    Process a single file for moving.

    Args:
        file_info (tuple): Contains (root, file, relative_path)

    Returns:
        str: Result message indicating success, warning, or error
    """
    root, file, relative_path = file_info
    try:
        # Split filename and extension
        file_base, file_ext = splitext(file)

        # Construct corresponding GT folder path
        gt_subfolder = os.path.join(GT_SOURCE, relative_path)

        # Check if GT folder exists
        if os.path.isdir(gt_subfolder):
            # Find GT files matching the base filename
            matched_files = []
            for gt_file in os.listdir(gt_subfolder):
                gt_base, _ = splitext(gt_file)
                if gt_base == file_base:
                    matched_files.append(gt_file)

            # If matching files found
            if matched_files:
                # Process image file
                image_source_path = os.path.join(root, file)
                image_target_subfolder = os.path.join(IMAGE_OK, relative_path)
                os.makedirs(image_target_subfolder, exist_ok=True)
                image_target_path = os.path.join(image_target_subfolder, file)

                # Process annotation file (only first match)
                gt_file = matched_files[0]
                gt_source_path = os.path.join(gt_subfolder, gt_file)
                gt_target_subfolder = os.path.join(GT_OK, relative_path)
                os.makedirs(gt_target_subfolder, exist_ok=True)
                gt_target_path = os.path.join(gt_target_subfolder, gt_file)

                # Move files
                shutil.move(image_source_path, image_target_path)
                shutil.move(gt_source_path, gt_target_path)
                return f"Success: Moved {image_source_path} -> {image_target_path}"

            else:
                return f"Warning: No matching annotation found for {file_base} (in {gt_subfolder})"
        else:
            return f"Warning: Corresponding GT folder does not exist: {gt_subfolder}"
    except Exception as e:
        return f"Error: Failed to process {file} - {str(e)}"


def main():
    """Main function to coordinate file processing."""
    # Collect all files to process
    file_list = []
    for root, _, files in os.walk(IMAGE_SOURCE):
        # Check if current path contains excluded folders
        current_relative_path = os.path.relpath(root, IMAGE_SOURCE)
        path_components = current_relative_path.split(os.sep)

        # Skip if any excluded folder is in the path
        if any(folder in path_components for folder in EXCLUDE_FOLDERS):
            print(f"Skipping excluded folder: {root}")
            continue

        # Calculate relative path
        relative_path = os.path.relpath(root, IMAGE_SOURCE)

        # Collect file information
        for file in files:
            file_list.append((root, file, relative_path))

    print(f"Found {len(file_list)} files to process")

    # Process files in parallel using ThreadPoolExecutor
    # Adjust max_workers based on system performance (typically 2-4x CPU cores)
    max_workers = min(32, os.cpu_count() * 4)  # Limit to max 32 workers
    print(f"Processing with {max_workers} threads")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = [executor.submit(process_file, file_info) for file_info in file_list]

        # Process results as they complete
        for future in as_completed(futures):
            print(future.result())

    print("All file processing completed")


if __name__ == "__main__":
    main()