import os
from collections import defaultdict

def check_image_existence(label_file, image_directory):
    # Images that do not exist
    missing_images = []
    # Count occurrences of each image path
    image_counts = defaultdict(int)
    line_count = 0

    # Open the file and read line by line
    with open(label_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        # Iterate through each line
        for line in lines:
            line_count += 1
            parts = line.strip().split('\t')

            # Check if there is a delimiter
            if len(parts) > 1:
                image_path = parts[0]
            else:
                image_path = parts[0]  # Use the entire line as the image path

            # Record the occurrence count of the image path
            image_counts[image_path] += 1

            # Check if the image exists
            if not os.path.exists(os.path.join(image_directory, image_path)):
                missing_images.append(image_path)
                print(f"Image {image_path} does not exist in the directory {image_directory}.")

            print(line_count)

    # Output duplicate image paths
    repeated_images = [path for path, count in image_counts.items() if count > 1]
    if repeated_images:
        print("\nThe following images are duplicated:")
        for image_path in repeated_images:
            print(image_path)
    else:
        print("\nNo duplicated images found.")

    return missing_images
