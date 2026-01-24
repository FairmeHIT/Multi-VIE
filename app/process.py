"""
Author: Huafu Li
Date: 2025-06-26
Description: Core service module for certificate image processing.
             Includes functions for image validation, classification using EfficientNetV2,
             information extraction with LLMs, and data post-processing.
"""

import logging
import time
import os
import sys
from typing import List, Dict, Tuple, Union, Optional

logger = logging.getLogger(__name__)

from app.llm import main_fig_VIE
from app.data_process import main_llm_data_postprocess
from app.data_process import fig_data_preprocess
from app.data_process import data_predefined
from app.json_extract import rule_json_extract

# Define status codes for this module
VIEW_CODE_OK = 200
VIEW_CODE_ALL_ERR = 400
VIEW_CODE_INVALID_FIG = 401


RESP_CODE_TIMEOUT = 101  # Request timeout
RESP_CODE_SVR_ERR = 102  # LLM service exception
RESP_CODE_FORMAT_ERR = 103  # LLM response format exception (e.g., hallucination, missing end flag)
RESP_CODE_OK = 200  # Success

# Error codes returned by local processing
RESP_CODE_NOCERTI = 104  # Not a target certificate
RESP_CODE_NOFIND = 105  # Not found in the file
RESP_CODE_CLASMODEL = 106  # Classification model error
RESP_CODE_ALL_ERR = 400  # Unified error code


def is_valid_non_empty_list(input_list: List) -> bool:
    """
    Check if the input is a valid non-empty list
    :param input_list: The input list to check
    :return: True if the input is a valid non-empty list, False otherwise
    """
    return input_list is not None and isinstance(input_list, list) and input_list


def check_input_fig_and_preprocess(img_paths_list: List[str]) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Validate input image paths and preprocess images.

    Args:
        img_paths_list (list): List of image paths.

    Returns:
        tuple: A tuple containing a list of valid image paths and a list of dictionaries
               with invalid image paths and error messages.
    """
    if not is_valid_non_empty_list(img_paths_list):
        logger.error(f"img_paths_list is not a valid non-empty list, value: {img_paths_list}")
        return [], [{"input_list": "img_paths_list is not a valid non-empty list"}]

    valid_fig_list: List[str] = []
    invalid_fig_list: List[Dict[str, str]] = []
    for img_path in img_paths_list:
        try:
            if not isinstance(img_path, str):
                error_msg = f"Input item is not a valid string path"
                logger.error(error_msg)
                invalid_fig_list.append({img_path: error_msg})
                continue

            img_name = os.path.basename(img_path)
            if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                result = fig_data_preprocess.process_image_size(img_path)
                if len(result) == 3 and isinstance(result[0], bool) and isinstance(result[1], str):
                    fig_size_ok, fig_path_temp, data_code = result
                    if fig_size_ok:
                        img_path = fig_path_temp
                        valid_fig_list.append(img_path)
                        # logger.info(f"Image processed successfully, file path: {img_path}, file name: {img_name}")
                    else:
                        error_msg = "Image size is too small for further processing"
                        invalid_fig_list.append({img_path: error_msg})
                        # logger.info(f"{error_msg}, file path: {img_path}, file name: {img_name}")
                else:
                    error_msg = f"fig_data_preprocess.process_image_size returned an incorrect format: {result}"
                    logger.error(error_msg)
                    invalid_fig_list.append({img_path: error_msg})
            else:
                error_msg = "Invalid image format. Please upload JPG, JPEG, or PNG images."
                logger.error(f"{error_msg} File path: {img_path}, file name: {img_name}")
                invalid_fig_list.append({img_path: error_msg})
        except Exception as e:
            error_msg = f"An unknown error occurred while processing input item {img_path}: {str(e)}"
            logger.error(error_msg)
            invalid_fig_list.append({img_path: error_msg})

    logger.info(f"Image processing completed. Valid images/total images: {len(valid_fig_list)}/{len(img_paths_list)}")
    return valid_fig_list, invalid_fig_list


def class_fig_list_using_efficientNetV2(valid_fig_list: List[str], target_cert_list: List[str], process_type: str,
                                        THRESHOLD_level1: float, THRESHOLD_level2: float, THRESHOLD: float,
                                        MAX_MATCHES: int, enhance_img: bool) -> Optional[
    List[Dict[str, Union[str, float]]]]:
    """
    Classify a list of valid images using EfficientNetV2.

    Args:
        valid_fig_list: List of valid image paths.
        target_cert_list: List of target certificate types.
        process_type: Processing type ("multiParallel" or other).
        THRESHOLD_level1: Threshold level 1 for classification.
        THRESHOLD_level2: Threshold level 2 for classification.
        THRESHOLD: General classification threshold.
        MAX_MATCHES: Maximum number of matches.
        enhance_img: Flag to enhance images before classification.

    Returns:
        List of dictionaries containing image information if successful, None otherwise.
    """
    # Check if input lists are valid and non-empty
    if not valid_fig_list:
        logger.error(f"valid_fig_list is not a valid non-empty list, value: {valid_fig_list}")
        return None
    if not target_cert_list:
        logger.error(f"target_cert_list is not a valid non-empty list, value: {target_cert_list}")
        return None

    # List to store image information
    img_info_list: List[Dict[str, Union[str, float]]] = []
    # Record start time
    tic = time.time()

    for img_path in valid_fig_list:
        try:
            # Check if the input item is a valid string path
            if not isinstance(img_path, str):
                logger.error(f"Input item {img_path} is not a valid string path")
                continue

            if process_type == "multiParallel":
                from app.figure_classification import main_fig_class_parallel_processing as main_fig_class
                # Classify the image using the model
                resp_code, cert_type_en, predict_prob = main_fig_class.run_model_efficientnet_v2_for_one_fig(
                    img_path, target_cert_list, THRESHOLD, MAX_MATCHES, enhance_img)
            else:
                # Classify the image using the model
                from app.figure_classification import main_fig_class_oneModel as main_fig_class
                resp_code, cert_type_en, predict_prob = main_fig_class.run_model_efficientnet_v2_for_one_fig(
                    img_path, target_cert_list, THRESHOLD_level1, THRESHOLD_level2, MAX_MATCHES, enhance_img)

            logger.info(f"cert_type_en={cert_type_en}, predict_prob={predict_prob}")
            if resp_code == RESP_CODE_OK:
                # If classification is successful, add image information to the list
                img_info_list.append({
                    "img_path": img_path,
                    "cert_type_en": cert_type_en,
                    "predict_prob": predict_prob
                })
            else:
                # If classification fails, log the error
                logger.info(f"main_fig_class.run_model_efficientnet_v2_for_one_fig returned an invalid code")
        except Exception as e:
            # Handle unknown errors
            logger.error(f"An unknown error occurred while processing input item {img_path}: {str(e)}")

    # Record end time
    toc = time.time()
    if img_info_list:
        # Log processing information if there are valid results
        logger.info(f"Completed classification of {len(valid_fig_list)} images in {toc - tic} seconds")
        logger.info(f"Classification results: {img_info_list}")
    else:
        # Log if no target classifications were found
        logger.info("No target classification results found.")

    return img_info_list if img_info_list else None


def vie_fig_list_using_llm(img_info_list: List[Dict[str, str]]) -> Union[List[Dict], None]:
    """
    Extract key information from images using a Large Language Model (LLM) and perform post-processing.

    Args:
        img_info_list: List containing image information (path and type).

    Returns:
        List of processed key information dictionaries if successful, None otherwise.
    """
    if not is_valid_non_empty_list(img_info_list):
        logger.info(f"img_info_list is not a valid non-empty list, value: {img_info_list}")
        return None

    cert_photo_list: List[Dict] = []
    for img_info in img_info_list:
        try:
            cert_type_en = img_info['cert_type_en']
            saved_dir = img_info['saved_dir']
            unique_name = img_info['unique_name']
            img_path = os.path.join(saved_dir, unique_name)
            result, llm_resp_code = main_fig_VIE.call_llm_interface(img_path, cert_type_en)
            logger.info(
                f"Return code from call_llm_interface: {llm_resp_code}, content: {result}, image info: {img_info}")

            if result:
                photorealistic_i, data_resp_code = main_llm_data_postprocess.llm_data_postprocess(cert_type_en, result)
                if data_resp_code == RESP_CODE_OK:
                    cert_photo_list.append(photorealistic_i)
                else:
                    logger.error(f"Data post-processing failed, return code: {data_resp_code}, image info: {img_info}")
            else:
                logger.error(f"LLM interface call failed, return code: {result}, image info: {img_info}")
        except KeyError:
            logger.error(f"Missing 'img_path' or 'cert_type_en' key in input item {img_info}")
        except Exception as e:
            logger.error(f"An unknown error occurred while processing input item {img_info}: {str(e)}")

    return cert_photo_list if cert_photo_list else None


def check_input_target_cert_and_preprocess(target_cert_from_json: List[Dict[str, str]]) -> Union[List[str], None]:
    """
    Validate and preprocess the input list of target certificates.

    Args:
        target_cert_from_json (list): List of target certificates from JSON.

    Returns:
        list: Preprocessed list of target certificates, or None if empty or invalid.
    """
    if not is_valid_non_empty_list(target_cert_from_json):
        logger.error(f"target_cert_from_json is not a valid non-empty list, value: {target_cert_from_json}")
        return None

    target_cert_list: List[str] = []
    for item in target_cert_from_json:
        try:
            lic_name = item['lic_name']
            if lic_name and lic_name in data_predefined.target_type_list_en:
                target_cert_list.append(lic_name)
        except KeyError:
            logger.error(
                f"Error in check_input_target_cert_and_preprocess, missing 'lic_name' key in input item {item}")
        except Exception as e:
            logger.error(
                f"Error in check_input_target_cert_and_preprocess, unknown error processing input item {item}: {str(e)}")

    return target_cert_list if target_cert_list else None