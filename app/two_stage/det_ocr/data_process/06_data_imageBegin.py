import os

def check_image_lines(input_file):
    # Lines that do not start with 'image/'
    non_image_lines = []

    # Open the file and read line by line
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        # Iterate through each line
        for line_number, line in enumerate(lines, start=1):
            # Check if the line starts with 'image/'
            if not line.startswith('image/'):
                non_image_lines.append((line_number, line.strip()))
                print(f"Line {line_number}: {line.strip()} (does not start with 'image/')")

    return non_image_lines