import os

def merge_txt_files(input_dir, output_file):
    # Initialize an empty string to store all text content
    merged_content = ""

    # Iterate through the specified directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            # Construct the full file path
            file_path = os.path.join(input_dir, filename)

            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Append the content to merged_content
                merged_content += content + '\n'  # Add a newline to separate content from different files

    # Write the merged content to a new file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(merged_content)
        print(f"All text files have been merged into {output_file}")