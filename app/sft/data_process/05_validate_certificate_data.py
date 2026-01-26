import os
import json
import shutil
from pathlib import Path

# Define paths
# TODO: Replace these placeholder paths with your actual directory paths
TRAIN_IMAGE_OK = "<TRAIN_IMAGE_OK_PATH>"
TRAIN_GT_OK = "<TRAIN_GT_OK_PATH>"
TRAIN_IMAGE_FAILED = "<TRAIN_IMAGE_FAILED_PATH>"
TRAIN_GT_FAILED = "<TRAIN_GT_FAILED_PATH>"

# Mapping of certificate type IDs to English names
target_type_num_mapping_en = {
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

# Required fields for each certificate type
# These are the expected keys that should be present in the 'result' field of the JSON
# examples
text_prompt_templates = {
    1: "\"获证单位名称\", \"首次发证日期\", \"本次发证日期\", \"有效期截止日期\", \"符合标准\", \"是否有签字\", \"是否有盖章\", \"印章名称\"",
    2: "\"获证单位名称\", \"首次发证日期\", \"本次发证日期\", \"有效期截止日期\", \"符合标准\", \"是否有签字\", \"是否有盖章\", \"印章名称\"",
    3: "\"获证单位名称\", \"首次发证日期\", \"本次发证日期\", \"有效期截止日期\", \"符合标准\", \"是否有签字\", \"是否有盖章\", \"印章名称\"",
    4: "\"获证单位名称\", \"首次发证日期\", \"本次发证日期\", \"有效期截止日期\", \"符合标准\", \"是否有签字\", \"是否有盖章\", \"印章名称\"",
    5: "\"获证单位名称\", \"首次发证日期\", \"本次发证日期\", \"有效期截止日期\", \"符合标准\", \"是否有签字\", \"是否有盖章\", \"印章名称\"",
    6: "\"单位名称\", \"统一社会信用代码\", \"住所\", \"营业期限\", \"法定代表人\", \"注册资本\", \"经营范围\", \"是否有盖章\", \"登记机关印章名称\"",
    7: "\"单位名称\", \"统一社会信用代码\", \"注册地址\", \"营业期限\", \"法定代表人\", \"开办资金\", \"是否有盖章\", \"登记机关印章名称\"",
    8: "\"单位名称\", \"投保人姓名\", \"社会保障号码\", \"险种\", \"缴费起始年月\", \"缴费截止年月\", \"本单位实际缴费月数\", \"是否有盖章\", \"印章名称\"",
    9: "\"姓名\", \"身份证号\", \"性别\", \"出生日期\"",
    10: "\"获证人姓名\", \"性别\", \"出生日期\", \"专业名称\", \"学历等级\", \"毕业时间\", \"证书编号\", \"学校名称\", \"是否有签字\", \"是否有盖章\", \"印章名称\"",
    11: "\"获证人姓名\", \"性别\", \"出生日期\", \"专业名称\", \"学位等级\", \"毕业时间\", \"证书编号\", \"学校名称\", \"是否有签字\"",
    12: "\"获证单位\", \"发证单位\", \"符合标准\", \"首次获证日期\", \"本次发证日期\", \"有效期\", \"证书等级\", \"是否有签字\", \"是否有盖章\", \"印章名称\"",
    13: "\"获证单位\", \"发证单位\", \"符合标准\", \"首次获证日期\", \"本次发证日期\", \"有效期\", \"证书等级\", \"是否有签字\", \"是否有盖章\", \"印章名称\"",
    14: "\"获证单位\", \"发证单位\", \"符合标准\", \"首次获证日期\", \"本次发证日期\", \"有效期\", \"证书等级\", \"是否有签字\", \"是否有盖章\", \"印章名称\"",
    15: "\"获证单位\", \"发证单位\", \"符合标准\", \"首次获证日期\", \"本次发证日期\", \"有效期\", \"证书等级\", \"是否有签字\", \"是否有盖章\", \"印章名称\""
}

# Maximum allowed number of unidentified fields (can be adjusted as needed)
MAX_UNIDENTIFIED_COUNT = 3

def get_type_id(type_name):
    """
    Get the corresponding ID from the type name.

    Args:
        type_name (str): The English name of the certificate type.

    Returns:
        int or None: The corresponding ID if found, None otherwise.
    """
    for id, name in target_type_num_mapping_en.items():
        if name == type_name:
            return id
    return None

def get_required_fields(type_id):
    """
    Get the list of required fields based on the type ID.

    Args:
        type_id (int): The ID of the certificate type.

    Returns:
        list: A list of required field names (in Chinese).
    """
    if type_id not in text_prompt_templates:
        return []

    # Parse the template string to get the field list
    template = text_prompt_templates[type_id]
    # Remove quotes and split fields
    fields = [field.strip().strip('"') for field in template.split(',')]
    return fields

def create_directory(path):
    """
    Create a directory if it does not exist.

    Args:
        path (str): The path of the directory to create.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def move_files(json_path, image_path, target_type, simulate=False):
    """
    Move files to the failed directory.

    Args:
        json_path (str): Path to the JSON file.
        image_path (str): Path to the corresponding image file.
        target_type (str): Name of the target type folder.
        simulate (bool): If True, only simulate the move without actually performing it. Defaults to False.

    Returns:
        bool: Always returns True to indicate the file has been (or would be) moved.
    """
    # Create target directories
    target_image_dir = os.path.join(TRAIN_IMAGE_FAILED, target_type)
    target_gt_dir = os.path.join(TRAIN_GT_FAILED, target_type)

    if not simulate:
        create_directory(target_image_dir)
        create_directory(target_gt_dir)
    else:
        print(f"[SIMULATE] Would create directory: {target_image_dir}")
        print(f"[SIMULATE] Would create directory: {target_gt_dir}")

    # Move image file
    if os.path.exists(image_path):
        target_image_path = os.path.join(target_image_dir, os.path.basename(image_path))
        if simulate:
            print(f"[SIMULATE] Would move image: {image_path} -> {target_image_path}")
        else:
            shutil.move(image_path, target_image_path)
            print(f"Moved image: {image_path} -> {target_image_path}")

    # Move JSON file
    if os.path.exists(json_path):
        target_json_path = os.path.join(target_gt_dir, os.path.basename(json_path))
        if simulate:
            print(f"[SIMULATE] Would move JSON: {json_path} -> {target_json_path}")
        else:
            shutil.move(json_path, target_json_path)
            print(f"Moved JSON: {json_path} -> {target_json_path}")

    return True

def check_json_file(json_path, simulate=False):
    """
    Check if a JSON file meets the requirements.

    Args:
        json_path (str): Path to the JSON file.
        simulate (bool): If True, only simulate the move without actually performing it. Defaults to False.

    Returns:
        bool: True if all checks passed, False otherwise (or if the file was moved).
    """
    # Get the subfolder name (certificate type) where the file is located
    dir_name = os.path.basename(os.path.dirname(json_path))

    # Get the corresponding image path
    file_name = os.path.splitext(os.path.basename(json_path))[0]
    # Try common image extensions
    image_extensions = ['.png', '.jpg', '.jpeg']
    image_path = None

    for ext in image_extensions:
        potential_path = os.path.join(TRAIN_IMAGE_OK, dir_name, f"{file_name}{ext}")
        if os.path.exists(potential_path):
            image_path = potential_path
            break

    if not image_path:
        print(f"Warning: Corresponding image file for {json_path} not found.")
        return False

    try:
        # Read the JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check 1: Does the 'type' value match the folder name?
        if 'type' not in data or data['type'] != dir_name:
            print(f"Error: 'type' value in {json_path} does not match folder name '{dir_name}'.")
            return move_files(json_path, image_path, dir_name, simulate)

        # Check 2: Does the 'result' field exist?
        if 'result' not in data:
            print(f"Error: Missing 'result' field in {json_path}.")
            return move_files(json_path, image_path, dir_name, simulate)

        result = data['result']

        # Get type ID and required fields
        type_id = get_type_id(dir_name)
        if not type_id:
            print(f"Error: Unknown certificate type '{dir_name}'.")
            return move_files(json_path, image_path, dir_name, simulate)

        required_fields = get_required_fields(type_id)

        if not required_fields:
            print(f"Error: No required fields defined for type '{dir_name}'.")
            return move_files(json_path, image_path, dir_name, simulate)

        # Check 3: Does the 'result' field contain all required keys and no extra keys?
        result_keys = set(result.keys())
        required_set = set(required_fields)

        if result_keys != required_set:
            missing = required_set - result_keys
            extra = result_keys - required_set

            error_msg = f"Error: 'result' field in {json_path} does not meet requirements."
            if missing:
                error_msg += f" Missing fields: {', '.join(missing)}"
            if extra:
                error_msg += f" Extra fields: {', '.join(extra)}"

            print(error_msg)
            return move_files(json_path, image_path, dir_name, simulate)

        # Check 4: Check the number of unidentified fields
        unidentified_count = 0
        for field, value in result.items():
            if value in ['unidentified', '未识别到']:
                unidentified_count += 1

        if unidentified_count > MAX_UNIDENTIFIED_COUNT:
            print(f"Error: Too many unidentified fields in {json_path} ({unidentified_count}/{MAX_UNIDENTIFIED_COUNT}).")
            return move_files(json_path, image_path, dir_name, simulate)

        # All checks passed
        print(f"Check passed: {json_path}")
        return True

    except json.JSONDecodeError:
        print(f"Error: {json_path} is not a valid JSON file.")
        return move_files(json_path, image_path, dir_name, simulate)
    except Exception as e:
        print(f"Error processing {json_path}: {str(e)}")
        return move_files(json_path, image_path, dir_name, simulate)

def main(simulate=False):
    """
    Main function to orchestrate the checking process.

    Args:
        simulate (bool): If True, runs in simulation mode without making changes. Defaults to False.
    """
    # Create failed folders if they don't exist
    if not simulate:
        create_directory(TRAIN_IMAGE_FAILED)
        create_directory(TRAIN_GT_FAILED)
    else:
        print(f"[SIMULATE] Would create failed folders: {TRAIN_IMAGE_FAILED} and {TRAIN_GT_FAILED}")

    # Traverse all JSON files in the GT folders
    for root, dirs, files in os.walk(TRAIN_GT_OK):
        for file in files:
            if file.lower().endswith('.json'):
                json_path = os.path.join(root, file)
                check_json_file(json_path, simulate)

    print("Processing complete.")

if __name__ == "__main__":
    # Set to True for testing (simulate moves without actually moving files)
    # Set to False for actual operation
    main(simulate=False) # Change this line to switch between simulation and actual run modes