import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Document type mapping: ID to English name
# Constants should be placed at the module level
TYPE_ENGLISH_MAP = {
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

# Document type mapping: English to Chinese
TYPE_CHINESE_MAP = {
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

def validate_gt_data(gt_data: Dict[str, Any]) -> bool:
    """
    Validate the legality of the ground truth (annotation) data.

    Args:
        gt_data (Dict[str, Any]): The annotation data loaded from a JSON file.

    Returns:
        bool: True if the data is valid, False otherwise.
    """
    if not isinstance(gt_data, dict):
        logger.error("Annotation data format error. Expected a dictionary.")
        return False

    if 'type' not in gt_data:
        logger.error("Annotation data is missing the 'type' field.")
        return False

    if 'result' not in gt_data or not isinstance(gt_data['result'], dict):
        logger.error("Annotation data is missing a valid 'result' field.")
        return False

    return True

def find_corresponding_gt_file(img_path: Path, image_root: Path, gt_root: Path) -> Optional[Path]:
    """
    Find the corresponding annotation (JSON) file for a given image.

    Args:
        img_path (Path): Path to the image file.
        image_root (Path): Root directory containing image files.
        gt_root (Path): Root directory containing annotation files.

    Returns:
        Optional[Path]: Path to the annotation file if found, None otherwise.
    """
    try:
        # Calculate the relative path from the image root to the image
        rel_path = img_path.relative_to(image_root)
        # Construct the expected path to the annotation file
        gt_path = gt_root / rel_path.parent / f"{img_path.stem}.json"

        if gt_path.exists() and gt_path.is_file():
            return gt_path
        return None
    except ValueError:
        logger.error(f"Image path is not under the specified image root directory: {img_path}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while searching for the annotation file: {str(e)}")
        return None

def collect_image_files(image_root: Path, extensions: List[str] = None) -> List[Path]:
    """
    Collect all image files with specified extensions from the root directory and subdirectories.

    Args:
        image_root (Path): Root directory to search for images.
        extensions (List[str], optional): List of image file extensions (e.g., ['png', 'jpg']).
            If None, defaults to ['png', 'jpg', 'jpeg'].

    Returns:
        List[Path]: A sorted list of unique Path objects to image files.
    """
    if not extensions:
        extensions = ['png', 'jpg', 'jpeg']

    image_files = []
    for ext in extensions:
        # Use pathlib's glob method to find files recursively
        pattern = f"**/*.{ext}"
        image_files.extend(image_root.glob(pattern))

    # Remove duplicates and sort
    unique_files = sorted(list(set(image_files)))

    logger.info(f"Found {len(unique_files)} image files in total.")
    return unique_files

def build_certificate_dataset(
        image_root: str,
        gt_root: str,
        output_file: str,
        image_extensions: List[str] = None
) -> None:
    """
    Build a structured dataset for certificate key information extraction tasks.

    This function processes pairs of image and annotation files, validates them,
    and constructs a JSON dataset file in a specific format suitable for model training.

    Args:
        image_root (str): Path to the root directory containing image files.
        gt_root (str): Path to the root directory containing annotation (JSON) files.
        output_file (str): Path to the output JSON dataset file.
        image_extensions (List[str], optional): List of image file extensions to consider.
    """
    # Convert string paths to Path objects for easier manipulation
    image_root_path = Path(image_root)
    gt_root_path = Path(gt_root)
    output_path = Path(output_file)

    # Validate input directories
    if not image_root_path.exists() or not image_root_path.is_dir():
        logger.error(f"Image root directory does not exist or is not a directory: {image_root}")
        return

    if not gt_root_path.exists() or not gt_root_path.is_dir():
        logger.error(f"Annotation root directory does not exist or is not a directory: {gt_root}")
        return

    # Create output directory if it doesn't exist
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # Collect all image files
    image_files = collect_image_files(image_root_path, image_extensions)
    if not image_files:
        logger.warning("No image files found for processing.")
        return

    dataset = []
    success_count = 0
    skip_count = 0

    # Process each image file
    for img_path in image_files:
        try:
            # Find the corresponding annotation file
            gt_file = find_corresponding_gt_file(img_path, image_root_path, gt_root_path)
            if not gt_file:
                logger.warning(f"Corresponding annotation file not found, skipping: {img_path}")
                skip_count += 1
                continue

            # Read the annotation file
            with open(gt_file, 'r', encoding='utf-8') as f:
                try:
                    gt_data = json.load(f)
                except json.JSONDecodeError as e:
                    logger.error(f"Annotation file has invalid JSON format: {gt_file}, Error: {str(e)}")
                    skip_count += 1
                    continue

            # Validate the annotation data structure
            if not validate_gt_data(gt_data):
                logger.error(f"Invalid annotation data: {gt_file}")
                skip_count += 1
                continue

            # Get document type information
            cert_type_en = gt_data.get('type')
            if cert_type_en not in TYPE_CHINESE_MAP:
                logger.warning(f"Unknown document type: '{cert_type_en}', File: {gt_file}")
                cert_type_zh = cert_type_en  # Use the original type if unknown
            else:
                cert_type_zh = TYPE_CHINESE_MAP[cert_type_en]

            # Get the list of fields to extract
            result_fields = list(gt_data.get('result', {}).keys())
            fields_str = '、'.join(result_fields)

            # Construct a training data item
            item = {
                "name": img_path.stem,
                "task": "证照关键信息提取",
                "type": cert_type_zh,
                "images": [
                    str(img_path)
                ],
                "messages": [
                    {
                        "role": "user",
                        "content": (f"<image>识别并提取图片中「{cert_type_zh}」的关键信息，严格按要求返回：\n"
                                    f"1. 需提取的字段清单：{fields_str}；\n"
                                    "2. 填充规则：\n"
                                    "   - 字段信息清晰可识别：填写具体内容（与图片一致）；\n"
                                    "   - 字段信息缺失/模糊/未出现：填写null（禁止推测/编造内容）；\n"
                                    "   - 布尔型字段：仅返回true（明确识别到）或false（未识别到）；\n"
                                    "3. 格式要求：仅返回标准JSON，不额外添加文字说明，不包含字段清单外的信息。")
                    },
                    {
                        "role": "assistant",
                        "content": f"```json\n{json.dumps(gt_data.get('result', {}), ensure_ascii=False)}\n```"
                    }
                ]
            }

            dataset.append(item)
            success_count += 1
            if success_count % 100 == 0:  # Print progress every 100 files processed
                logger.info(f"Processed {success_count} files successfully.")

        except Exception as e:
            logger.error(f"An error occurred while processing {img_path}: {str(e)}")
            skip_count += 1
            continue

    # Save the constructed dataset
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    logger.info(f"Dataset construction completed.")
    logger.info(f"Successfully processed {success_count} samples, skipped {skip_count} samples.")
    logger.info(f"Dataset saved to: {output_path}")

if __name__ == "__main__":
    # Configuration parameters - can be modified to read from a config file or command-line arguments
    config = {
        "image_root": "<IMAGE_ROOT_DIRECTORY>",
        "gt_root": "<ANNOTATION_ROOT_DIRECTORY>",
        "output_file": "<OUTPUT_DATASET_FILE_PATH>",
        "image_extensions": ['png', 'jpg', 'jpeg']
    }

    build_certificate_dataset(
        image_root=config["image_root"],
        gt_root=config["gt_root"],
        output_file=config["output_file"],
        image_extensions=config["image_extensions"]
    )