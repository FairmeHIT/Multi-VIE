import logging
import uuid
import time
import hashlib
import os
import re
import requests
import json
import base64
import sys
from typing import Dict, Optional, Tuple, Union
from app.llm.gyl_rotate_image_v2 import ImageOrientationRotator
from app.data_process import data_predefined
from app.llm import gen_result_call_llm

logger = logging.getLogger(__name__)

# Status codes
LLM_CODE_OK = 200  # Success
LLM_CODE_TIMEOUT = 101  # Timeout
LLM_CODE_SER_ERR = 102  # Service error
LLM_CODE_FORMAT_ERR = 103  # Format error
LLM_CODE_ALL_ERR = 400  # Other errors

# Initialize image rotation model
rotator = ImageOrientationRotator()


def run_kie_fun(cert_type_num: int, image_path: str) -> Tuple[Optional[Dict], int]:
    """
    Extract key information from certificate image using LLM.

    Args:
        cert_type_num: Certificate type ID
        image_path: Path to certificate image

    Returns:
        Tuple of extracted data (or None) and status code
    """
    # Input validation
    if not isinstance(cert_type_num, int):
        logger.error("Certificate type must be integer")
        return None, LLM_CODE_ALL_ERR
    if not isinstance(image_path, str):
        logger.error("Image path must be string")
        return None, LLM_CODE_ALL_ERR

    # Get certificate type name
    cert_type_zh = data_predefined.target_type_num_mapping_zh.get(
        cert_type_num, "Unknown certificate type"
    )
    logger.info(f"Processing {cert_type_zh} certificate")

    # Build prompt template
    text_for_kie = data_predefined.text_prompt_templates.get(
        cert_type_num, "Unknown certificate type"
    )
    text_for_kie = f"This is a {cert_type_zh} certificate. {text_for_kie}"

    # Rotate image if necessary
    try:
        rotated_image_path = rotator.rotate_image_by_orientation(image_path)
        if rotated_image_path:
            image_path = rotated_image_path
    except Exception as e:
        logger.error(f"Image rotation failed: {e}")

    # Encode image to base64
    try:
        with open(image_path, "rb") as f:
            base64_image = f"data:image;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    except Exception as e:
        logger.error(f"Failed to read image: {e}")
        return None, LLM_CODE_ALL_ERR

    # Call LLM for information extraction
    try:
        response, status_code = gen_result_call_llm.gen_result(
            base64_image, text_for_kie, data_predefined.llm_extract_sys_text
        )
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return None, LLM_CODE_ALL_ERR

    logger.info(f"KIE task completed: {response}")
    return response, status_code


def generate_result_dict(
        image_path: str,
        cert_type_num: int,
        resp_code: int,
        resp_msg: str,
        result: Optional[Dict]
) -> Dict:
    """Generate standardized result dictionary"""
    return {
        'name': os.path.basename(image_path),
        'type': cert_type_num,
        'path': os.path.dirname(image_path),
        'resp_code': resp_code,
        'resp_msg': resp_msg,
        'result': result
    }


def process_image_with_params(image_path: str, cert_type_num: int) -> Union[Dict, None]:
    """
    Process image with given certificate type.

    Args:
        image_path: Path to certificate image
        cert_type_num: Certificate type ID

    Returns:
        Result dictionary or None on error
    """
    # Input validation
    if not isinstance(cert_type_num, int):
        logger.error("Certificate type must be integer")
        return None
    if not isinstance(image_path, str):
        logger.error("Image path must be string")
        return None

    logger.info(f"Starting LLM processing")
    tic = time.time()

    try:
        # Extract information
        response, status_code = run_kie_fun(cert_type_num, image_path)

        # Handle errors
        if response is None:
            error_msgs = {
                LLM_CODE_TIMEOUT: 'LLM request timed out',
                LLM_CODE_SER_ERR: 'LLM service error',
                LLM_CODE_FORMAT_ERR: 'Invalid LLM response format'
            }
            return generate_result_dict(
                image_path, cert_type_num, status_code,
                error_msgs.get(status_code, 'Unknown error'), None
            )

        # Process successful result
        result_dict = generate_result_dict(
            image_path, cert_type_num, LLM_CODE_OK, 'Success', response
        )
        result_dict['result']['证书名称'] = data_predefined.target_type_num_mapping_zh.get(cert_type_num)

        toc = time.time()
        logger.info(f"KIE task completed in {toc - tic:.2f}s")
        return result_dict

    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        return generate_result_dict(
            image_path, cert_type_num, LLM_CODE_ALL_ERR, 'Failed', None
        )


def call_llm_interface(image_path: str, cert_type_en: str) -> Tuple[Optional[Dict], int]:
    """
    Interface to call LLM for certificate information extraction.

    Args:
        image_path: Path to certificate image
        cert_type_en: Certificate type (English)

    Returns:
        Tuple of result dictionary (or None) and status code
    """
    # Input validation
    if not isinstance(image_path, str):
        logger.error("Image path must be string")
        return None, LLM_CODE_ALL_ERR
    if not isinstance(cert_type_en, str):
        logger.error("Certificate type must be string")
        return None, LLM_CODE_ALL_ERR

    logger.info(f"Calling LLM interface for {image_path}")

    # Map certificate type to ID
    cert_type_num = next(
        (key for key, val in data_predefined.target_type_num_mapping_en.items() if val == cert_type_en),
        None
    )

    if cert_type_num is None:
        logger.error(f"Certificate type not found: {cert_type_en}")
        return None, LLM_CODE_ALL_ERR

    try:
        result_dict = process_image_with_params(image_path, cert_type_num)
        code_call_llm = result_dict['resp_code']
        logger.info(f"LLM response: {result_dict}, code: {code_call_llm}")
        return result_dict, code_call_llm

    except Exception as e:
        logger.error(f"LLM interface error: {e}, image: {image_path}")
        return None, LLM_CODE_ALL_ERR