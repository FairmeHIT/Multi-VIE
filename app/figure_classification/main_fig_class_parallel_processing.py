import json
import logging
import time
from datetime import datetime, timedelta
import shutil
import os
import schedule
import math
import uuid
import numpy as np
from typing import Dict, Tuple, Optional, List

import concurrent.futures
import threading

from app.figure_classification.code.efficientNetV2 import efficientNetV2
from app.figure_classification.class_ocr_rapidOCR import OCR_ModelManager
from app.data_process import image_preprocessing_for_ocr

logger = logging.getLogger(__name__)

# Error codes from gyl_llm
RESP_CODE_TIMEOUT = 101  # Request timeout
RESP_CODE_SVR_ERR = 102  # LLM service error
RESP_CODE_FORMAT_ERR = 103  # LLM response format error

# Local error codes
RESP_CODE_OK = 200  # Success
RESP_CODE_NOCERTI = 104  # Not a target certificate
RESP_CODE_NOFIND = 105  # Not found in file
RESP_CODE_CLASMODEL = 106  # Classification model error
RESP_CODE_ALL_ERR = 400  # General error

# Model and media paths
MODELS_PATH = '/data/models/efficientNetV2/'
MEDIA_ROOT_FOR_ES = "/data/c_result/"
MEDIA_ROOT_FOR_ME = "/data/fig_media/"


class EfficientNetV2Modeler:
    def __init__(self):
        self.class_indices_dict: Dict[str, Dict] = {}
        self.models_dict: Dict[str, object] = {}
        self.model_state: bool = False
        self.initialize_models()

    def initialize_models(self) -> None:
        """Initialize classification models if not loaded"""
        if not self.model_state:
            try:
                self.class_indices_dict, self.models_dict = self.load_model_efficientNetV2()
                self.model_state = bool(self.models_dict)
                logger.info("EfficientNetV2 models loaded successfully")
            except Exception as e:
                self.model_state = False
                logger.error(f"Failed to initialize models: {str(e)}")

    def load_model_efficientNetV2(self) -> Tuple[Dict[str, Dict], Dict[str, object]]:
        """
        Load all EfficientNetV2 classification models

        Returns:
            Tuple of class indices dictionary and models dictionary
        """
        try:
            tic = time.time()
            class_indices = {}
            models = {}

            if os.path.exists(MODELS_PATH):
                for item in os.listdir(MODELS_PATH):
                    model_subpath = os.path.join(MODELS_PATH, item)
                    if os.path.isdir(model_subpath):
                        # Load class indices
                        class_indices_path = os.path.join(model_subpath, 'class_indices.json')
                        try:
                            with open(class_indices_path, "r") as f:
                                class_indices[item] = json.load(f)
                            num_classes = len(class_indices[item])
                        except (FileNotFoundError, json.JSONDecodeError) as e:
                            logger.error(f"Error loading class indices for {item}: {str(e)}")
                            continue

                        # Load model
                        model_path = os.path.join(model_subpath, 'model.pth')
                        try:
                            model = gyl_efficientNetV2.load_model(model_path, num_classes)
                            models[item] = model
                        except Exception as e:
                            logger.error(f"Error loading model {item}: {str(e)}")
            else:
                logger.error(f"Models directory not found: {MODELS_PATH}")

            toc = time.time()
            logger.info(f"Models loaded in {toc - tic:.2f}s")
            return class_indices, models
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return {}, {}


def get_img_uuid(img_path: str) -> str:
    """Generate unique filename for image"""
    if not img_path:
        logger.error("img_path is required")
        return None

    unique_id = str(uuid.uuid4())
    file_extension = os.path.splitext(img_path)[1].lower()
    return f"{unique_id}{file_extension}"


def fig_process_save(
        img_path: str,
        new_filename: str,
        media_root_str: str,
        folder_name: str,
        lic_clas: str,
        project_id: str,
        package_id: str,
        supplier_id: str,
        file_type: str
) -> Optional[str]:
    """
    Save image to specified directory

    Args:
        img_path: Path to source image
        new_filename: Generated unique filename
        media_root_str: Root directory type ("MEDIA_ROOT_FOR_ME" or "MEDIA_ROOT_FOR_ES")
        folder_name: Subfolder name
        lic_clas: License classification
        project_id, package_id, supplier_id, file_type: ES metadata

    Returns:
        Saved directory path or None on error
    """
    if not img_path or not new_filename:
        logger.error("img_path and new_filename are required")
        return None

    try:
        if media_root_str == "MEDIA_ROOT_FOR_ME":
            current_date = datetime.now().strftime("%Y-%m-%d")
            if folder_name:
                date_folder_path = os.path.join(MEDIA_ROOT_FOR_ME, current_date, folder_name)
            else:
                date_folder_path = os.path.join(MEDIA_ROOT_FOR_ME, current_date)

            save_folder = os.path.join(date_folder_path, lic_clas) if lic_clas else date_folder_path

        elif media_root_str == "MEDIA_ROOT_FOR_ES":
            if not all([project_id, package_id, supplier_id, file_type]):
                logger.error("project_id, package_id, supplier_id, and file_type are required for ES storage")
                return None
            save_folder = os.path.join(MEDIA_ROOT_FOR_ES, project_id, package_id, supplier_id, file_type)
        else:
            logger.error("Invalid media_root_str. Must be 'MEDIA_ROOT_FOR_ME' or 'MEDIA_ROOT_FOR_ES'")
            return None

        # Create directory and save image
        os.makedirs(save_folder, exist_ok=True)
        saved_img_path = os.path.join(save_folder, new_filename)
        shutil.copy2(img_path, saved_img_path)

        logger.info(f"Image saved to: {saved_img_path}")
        return save_folder

    except (FileNotFoundError, PermissionError) as e:
        logger.error(f"Error saving image: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error saving image: {str(e)}")
    return None


# Initialize model managers
efficientnetv2_model_manager = EfficientNetV2Modeler()
ocr_model_manager = OCR_ModelManager()


def run_model_efficientnet_v2_for_one_fig(
        img_path: str,
        target_cert_list: List[str],
        threshold: float,
        max_matches: int,
        enhance_img: bool
) -> Tuple[Optional[int], Optional[str], Optional[float]]:
    """
    Classify single image using EfficientNetV2 models (parallel version)

    Args:
        img_path: Path to image
        target_cert_list: List of target certificate types
        threshold: Confidence threshold
        max_matches: Maximum OCR matches
        enhance_img: Whether to preprocess image for OCR

    Returns:
        Tuple of (status_code, certificate_type, confidence_score)
    """
    # Initialize models
    efficientnetv2_model_manager.initialize_models()
    ocr_model_manager.initialize_models()

    # Add special certificate types
    if "academicCertificate" in target_cert_list or "degreeCertificate" in target_cert_list:
        target_cert_list = list(set(target_cert_list + ["xuexinnet"]))

    logger.info(f"Starting parallel classification for: {target_cert_list}")
    tic = time.time()

    # Store parallel results
    results = {}
    lock = threading.Lock()

    def process_cert(target_cert):
        try:
            cert_type_en, predict_prob = gyl_efficientNetV2.clas_main(
                img_path,
                efficientnetv2_model_manager.class_indices_dict[target_cert],
                efficientnetv2_model_manager.models_dict[target_cert]
            )
            with lock:
                results[target_cert] = (cert_type_en, predict_prob)
        except Exception as e:
            logger.error(f"Error processing {target_cert}: {str(e)}")

    # Run parallel classification
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(target_cert_list)) as executor:
        futures = [executor.submit(process_cert, cert) for cert in target_cert_list]
        concurrent.futures.wait(futures)

    # Find best result
    best_cert = None
    best_prob = 0.0

    for target_cert, (cert_type_en, predict_prob) in results.items():
        if not cert_type_en or cert_type_en == 'others':
            continue

        if predict_prob > best_prob and predict_prob > threshold:
            best_cert = target_cert
            best_prob = predict_prob
            logger.info(f"New best: {target_cert}@{predict_prob:.4f}")

    logger.info(f"Best result: {best_cert}@{best_prob:.4f} for {img_path}")

    # Process best result with OCR
    if best_cert:
        cert_type_en, _ = results[best_cert]
        logger.info(f"Starting OCR refinement for {best_cert}")

        if enhance_img:
            logger.info(f"Preprocessing image for OCR: {img_path}")
            image_preprocessing_for_easy_ocr.preprocess_image_for_ocr(
                img_path,
                denoise=True,
                remove_bg=False,
                enhance_contrast=True,
                replace_original=True,
                debug=True
            )

        # OCR classification refinement
        ocr_result = ocr_model_manager.ocr_class_result(img_path, max_matches)
        logger.info(f"OCR result: {ocr_result}")

        if ocr_result and ocr_result in target_cert_list:
            img_type_en = ocr_result
            toc = time.time()
            logger.info(f"Classification completed in {toc - tic:.2f}s")
            return RESP_CODE_OK, img_type_en, best_prob

    # No valid classification
    toc = time.time()
    logger.info(f"No valid classification for {img_path}, time: {toc - tic:.2f}s")
    return RESP_CODE_NOCERTI, None, None