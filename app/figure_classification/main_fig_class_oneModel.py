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
# from app.figure_classification.class_ocr import OCR_ModelManager

from app.data_process import image_preprocessing_for_ocr

logger = logging.getLogger(__name__)

# Error codes returned by the algorithm
RESP_CODE_TIMEOUT = 101  # Request timeout
RESP_CODE_SVR_ERR = 102  # LLM service exception
RESP_CODE_FORMAT_ERR = 103  # LLM response format exception
RESP_CODE_OK = 200  # Success

# Error codes returned by the algorithm
RESP_CODE_NOCERTI = 104  # Not the target certificate
RESP_CODE_NOFIND = 105  # Not found in the file
RESP_CODE_CLASMODEL = 106  # Classification model error
RESP_CODE_ALL_ERR = 400  # Unified error

# Image classification model path
MODELS_PATH = ""

# Classification image save addresses
MEDIA_ROOT_FOR_ES = ""
MEDIA_ROOT_FOR_ME = ""
MEDIA_ROOT_FOR_ME_all = ""

if not os.path.exists(MEDIA_ROOT_FOR_ES):
    os.makedirs(MEDIA_ROOT_FOR_ES, exist_ok=True)
if not os.path.exists(MEDIA_ROOT_FOR_ME):
    os.makedirs(MEDIA_ROOT_FOR_ME, exist_ok=True)
if not os.path.exists(MEDIA_ROOT_FOR_ME_all):
    os.makedirs(MEDIA_ROOT_FOR_ME_all, exist_ok=True)

class EfficientNetV2Modeler:
    def __init__(self):
        self.class_indices_dict: Dict[str, Dict] = {}
        self.models_dict: Dict[str, object] = {}
        self.model_state: bool = False
        self.initialize_models()

    def initialize_models(self) -> None:
        """Initialize models if not loaded"""
        if not self.model_state:
            try:
                self.class_indices_dict, self.models_dict = self.load_model_efficientNetV2()
                if self.models_dict:
                    self.model_state = True
                    logger.info("SPM model loaded successfully")
                else:
                    logger.error("Model loading failed, model dictionary is empty")
            except Exception as e:
                self.model_state = False
                logger.error(f"Error initializing model: {str(e)}")

    def load_model_efficientNetV2(self) -> Tuple[Dict[str, Dict], Dict[str, object]]:
        """Load all EfficientNetV2 models"""
        try:
            tic = time.time()

            if os.path.exists(MODELS_PATH):
                for item in os.listdir(MODELS_PATH):
                    model_subpath = os.path.join(MODELS_PATH, item)
                    if os.path.isdir(model_subpath):
                        class_indices_path = os.path.join(model_subpath, 'class_indices.json')
                        model_path = os.path.join(model_subpath, 'model.pth')

                    # Load JSON file
                    try:
                        with open(class_indices_path, "r") as f:
                            self.class_indices_dict[item] = json.load(f)
                        num_classes = len(self.class_indices_dict[item])
                    except FileNotFoundError:
                        logger.error(f"JSON file not found: {class_indices_path}")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parsing error: {str(e)}")
                    except Exception as e:
                        logger.error(f"Error loading JSON file: {str(e)}")

                    # Load model file
                    try:
                        model = gyl_efficientNetV2.load_model(model_path, num_classes)
                        self.models_dict[item] = model
                    except Exception as e:
                        logger.error(f"Error loading {item} model: {str(e)}")
            else:
                logger.info(f"Folder {MODELS_PATH} does not exist.")
            toc = time.time()
            logger.info(f"Model loading time: {toc - tic}s")
            return self.class_indices_dict, self.models_dict
        except Exception as e:
            logger.error(f"Error in load_model_efficientNetV2: {str(e)}")
            return {}, {}


def get_img_uuid(img_path: str) -> str:
    """Generate a unique filename for the image"""
    if not img_path:
        logger.error("img_path is required and cannot be None or empty.")
        return None

    unique_id = str(uuid.uuid4())
    file_extension = os.path.splitext(img_path)[1].lower()
    new_filename = f"{unique_id}{file_extension}"

    return new_filename


def fig_process_save(img_path: str, new_filename: str, media_root_str: str, folder_name: str, lic_clas: str,
                     project_id: str, package_id: str, supplier_id: str, file_type: str) -> str:
    """
    Save the image to the specified folder
    :param img_path: Image path
    :param new_filename: New filename
    :param media_root_str: Media root string
    :param folder_name: Folder name
    :param lic_clas: License classification
    :param project_id, package_id, supplier_id, file_type: For ES
    :return: Saved directory path, None if failed
    """
    if not img_path or not new_filename:
        logger.error("img_path and new_filename are required and cannot be None or empty.")
        return None

    # Map string to actual path
    media_root_map = {
        "MEDIA_ROOT_FOR_ME": MEDIA_ROOT_FOR_ME,
        "MEDIA_ROOT_FOR_ME_all": MEDIA_ROOT_FOR_ME_all,
        "MEDIA_ROOT_FOR_ES": MEDIA_ROOT_FOR_ES
    }
    media_root = media_root_map.get(media_root_str)
    if not media_root:
        logger.error("media_root_str must be one of: MEDIA_ROOT_FOR_ME, MEDIA_ROOT_FOR_ME_all, MEDIA_ROOT_FOR_ES")
        return None

    if media_root in [MEDIA_ROOT_FOR_ME, MEDIA_ROOT_FOR_ME_all]:
        current_date = datetime.now().strftime("%Y-%m-%d")
        if folder_name:
            date_folder_path = os.path.join(media_root, current_date, folder_name)
        else:
            date_folder_path = os.path.join(media_root, current_date)

        folder_path = os.path.join(date_folder_path, lic_clas) if lic_clas else date_folder_path
    elif media_root == MEDIA_ROOT_FOR_ES:
        if not project_id or not package_id or not supplier_id or not file_type:
            logger.error("project_id, package_id, supplier_id, and file_type are required for MEDIA_ROOT_FOR_ES")
            return None
        folder_path = os.path.join(media_root, project_id, package_id, supplier_id, file_type)
    else:
        logger.error("Invalid media_root_str")
        return None

    try:
        saved_img_path = os.path.join(folder_path, new_filename)
        os.makedirs(folder_path, exist_ok=True)
        shutil.copy2(img_path, saved_img_path)
        logger.info(f"Image saved to: {saved_img_path}")
        return folder_path
    except FileNotFoundError:
        logger.error(f"Source image not found: {img_path}")
    except PermissionError:
        logger.error(f"Permission denied to save image to {folder_path}")
    except Exception as e:
        logger.error(f"Error saving image: {e}")
    return None


# Instantiate model managers
efficientnetv2_model_manager = EfficientNetV2Modeler()
ocr_model_manager = OCR_ModelManager()


def run_model_efficientnet_v2_for_one_fig(img_path: str, target_cert_list: List[str], threshold_level1: float,
                                         threshold_level2: float, max_matches: int, enhance_img: bool) -> Tuple[Optional[int], Optional[str], Optional[float]]:
    """
    Classify a single image using EfficientNetV2 model
    :param img_path: Image path
    :param target_cert_list: List of target certificates
    :return: Response code, image type, probability
    """
    efficientnetv2_model_manager.initialize_models()
    ocr_model_manager.initialize_models()

    try:
        logger.info(f"Starting classification task for {img_path}")

        img_type_en: Optional[str] = None
        img_prob: Optional[float] = None

        # Special handling for xuexinnet
        if ("academicCertificate" in target_cert_list or "degreeCertificate" in target_cert_list) and "xuexinnet" not in target_cert_list:
            target_cert_list.append("xuexinnet")

        cert_type_en, predict_prob = gyl_efficientNetV2.clas_main(
            img_path,
            efficientnetv2_model_manager.class_indices_dict['one_model'],
            efficientnetv2_model_manager.models_dict['one_model']
        )

        fuzzy_cert_types = ['xuexinnet', 'ISO9000', 'ISO14000', 'ISO45001', 'OHSAS18001', 'SA8000',
                           'socialSecurityCertificate', 'CESSCN_risk_eval', 'CESSCN_design_inte',
                           'CESSCN_emergency_resp', 'CESSCN_safety_train']

        logger.info(f"Predicted: {cert_type_en}, Probability: {predict_prob}")
        img_prob = predict_prob

        if cert_type_en and predict_prob >= threshold_level1:
            if cert_type_en in target_cert_list:
                if cert_type_en in fuzzy_cert_types:
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

                    doc_type_en = ocr_model_manager.ocr_class_result(img_path, max_matches)
                    if doc_type_en and doc_type_en in target_cert_list:
                        img_type_en = doc_type_en
                    else:
                        return RESP_CODE_NOCERTI, None, None
                else:
                    img_type_en = cert_type_en

                logging.info(f"Target certificate found: {img_path}, Type: {img_type_en}, Probability: {img_prob}")
                return RESP_CODE_OK, img_type_en, img_prob

        elif cert_type_en and predict_prob >= threshold_level2:
            if cert_type_en in target_cert_list:
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

                doc_type_en = ocr_model_manager.ocr_class_result(img_path, max_matches)
                logger.info(f"OCR result: {doc_type_en}")
                if doc_type_en:
                    img_type_en = doc_type_en
                    if doc_type_en in target_cert_list:
                        return RESP_CODE_OK, img_type_en, img_prob

                return RESP_CODE_NOCERTI, None, None

        else:
            logger.info(f"Image {img_path} is not a target certificate. Predicted: {cert_type_en}, Probability: {predict_prob}")
            return RESP_CODE_NOCERTI, None, None

    except KeyError as ke:
        logger.error(f"KeyError: {str(ke)}, missing key in model or index dictionary.")
    except Exception as e:
        logger.error(f"Error in run_model_efficientnet_v2_for_one_fig: {str(e)}")

    return RESP_CODE_ALL_ERR, None, None