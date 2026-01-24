import os
import json

def validate_dataset(json_file_path):
    """
    Validates a certificate dataset JSON file for consistency and correctness.

    The validation checks include:
    1. Ensuring each record has image information.
    2. Verifying that the specified image file exists.
    3. Checking that the image's containing folder name is a valid certificate type.
    4. Confirming that the certificate type mentioned in the record matches the folder name.

    Args:
        json_file_path (str): Path to the dataset JSON file to validate.
    """
    # Mapping of certificate type IDs to English names
    type_english_map = {
        1: 'ISO9001',
        2: 'ISO14001',
        3: 'ISO45001',
        4: 'OHSAS18001',
        5: 'SA8000',
        6: 'businessLicense',
        7: 'legalLicense',
        8: 'socialSecurityCertificate',
        9: 'ID',
        10: 'academicCertificate',
        11: 'degreeCertificate',
        12: 'CESSCN_risk_eval',
        13: 'CESSCN_design_inte',
        14: 'CESSCN_emergency_resp',
        15: 'CESSCN_safety_train'
    }

    # Extract all valid English type names
    valid_types = set(type_english_map.values())

    # Load the dataset JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        print(f"Successfully loaded dataset with {len(dataset)} records.")
    except Exception as e:
        print(f"Failed to load dataset: {str(e)}")
        return

    # Record error information
    errors = []
    total_errors = 0

    # Iterate through each record
    for idx, item in enumerate(dataset):
        item_id = idx + 1
        item_name = item.get('name', f"Record {item_id}")

        try:
            # Check if there is image information
            if 'images' not in item or not item['images']:
                error_msg = f"{item_name}: Missing image information."
                errors.append(error_msg)
                total_errors += 1
                continue

            # Assuming the first image in the list is the primary one
            # Note: Adjusted to handle the case where 'images' contains paths directly (as strings)
            # This part was ambiguous; the code now checks both possibilities.
            image_path = None
            if isinstance(item['images'][0], dict):
                image_path = item['images'][0].get('image_path')
            elif isinstance(item['images'][0], str):
                image_path = item['images'][0]

            if not image_path:
                error_msg = f"{item_name}: Image path is empty or not found in the expected format."
                errors.append(error_msg)
                total_errors += 1
                continue

            if not os.path.exists(image_path):
                error_msg = f"{item_name}: Image does not exist at path - {image_path}"
                errors.append(error_msg)
                total_errors += 1
                continue # Skip further checks for this item if image is missing

            # Check if the type matches the folder name
            # Get the folder name where the image is located
            img_dir = os.path.dirname(image_path)
            folder_name = os.path.basename(img_dir)

            # Extract the English type from the user message
            en_type = None
            if 'messages' in item and item['messages']:
                user_message = next((msg for msg in item['messages'] if msg.get('role') == 'user'), None)
                if user_message:
                    user_content = user_message.get('content', '')
                    if isinstance(user_content, str) and '「' in user_content and '」' in user_content:
                        # Extract Chinese type name from the prompt
                        zh_type = user_content.split('「')[1].split('」')[0]
                        # Find the corresponding English type
                        en_type = next((eng for eng, chn in type_chinese_map.items() if chn == zh_type), None)

            # Check if the folder name is a valid type
            if folder_name not in valid_types:
                error_msg = f"{item_name}: Folder name '{folder_name}' is not a valid certificate type."
                errors.append(error_msg)
                total_errors += 1
            # Check if the extracted type matches the folder name
            elif en_type and folder_name != en_type:
                error_msg = f"{item_name}: Type mismatch - Folder name is '{folder_name}', but the record's type is '{en_type}'."
                errors.append(error_msg)
                total_errors += 1

        except Exception as e:
            error_msg = f"{item_name}: An error occurred during processing - {str(e)}"
            errors.append(error_msg)
            total_errors += 1

    # Output check results
    print(f"\nValidation completed. Found {total_errors} errors:")
    for i, error in enumerate(errors, 1):
        print(f"{i}. {error}")

    # Save error report
    error_report_path = os.path.splitext(json_file_path)[0] + "_error_report.txt"
    with open(error_report_path, 'w', encoding='utf-8') as f:
        f.write(f"Dataset Error Report - Total {total_errors} errors\n\n")
        for i, error in enumerate(errors, 1):
            f.write(f"{i}. {error}\n")

    print(f"\nError report saved to: {error_report_path}")
    print(f"Dataset validation complete. Valid records: {len(dataset) - total_errors}/{len(dataset)}")

# Mapping from Chinese to English certificate types (for reverse lookup)
type_chinese_map = {
    'ISO9001': 'ISO9001系列质量管理体系认证证书',
    'ISO14001': 'ISO14001族环境管理体系认证证书',
    'ISO45001': 'ISO45001认证证书',
    'OHSAS18001': 'OHSAS18001认证证书',
    'SA8000': 'SA8000认证证书',
    'businessLicense': '营业执照',
    'legalLicense': '事业单位法人证书',
    'socialSecurityCertificate': '社保证书',
    'ID': '身份证',
    'academicCertificate': '学历证书',
    'degreeCertificate': '学位证书',
    'CESSCN_risk_eval': '通信网络安全服务能力证书（风险评估）',
    'CESSCN_design_inte': '通信网络安全服务能力证书（设计与集成）',
    'CESSCN_emergency_resp': '通信网络安全服务能力证书（应急响应）',
    'CESSCN_safety_train': '通信网络安全服务能力证书（安全培训）'
}

if __name__ == "__main__":
    # Please replace this with your dataset JSON file path
    dataset_json_path = "<DATASET_JSON_FILE_PATH>"
    validate_dataset(dataset_json_path)