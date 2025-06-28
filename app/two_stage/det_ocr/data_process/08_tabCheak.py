import re

# Define input and output file paths
input_file_path = r''
output_file_path = r''

# Read the file
with open(input_file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Process each line
processed_lines = []
for line in lines:
    # Use regular expression to replace spaces or tabs before [{ with a tab character
    processed_line = re.sub(r'\s*\[{', r'\t[{', line)
    processed_lines.append(processed_line)

# Write the processed content to the output file
with open(output_file_path, 'w', encoding='utf-8') as file:
    file.writelines(processed_lines)