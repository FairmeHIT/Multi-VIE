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

from app.figure_classification.code.efficientNetV2 import efficientNetV2
from app.figure_classification.class_ocr_rapidOCR import OCR_ModelManager

# from app.figure_classification.class_ocr import OCR_ModelManager


logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.WARNING)

# Algorithm return error codes --- from gyl_llm
RESP_CODE_TIMEOUT = 101  # Request timeout
RESP_CODE_SVR_ERR = 102  # LLM service exception
RESP_CODE_FORMAT_ERR = 103  # LLM return format exception (such as hallucination, no end marker returned)
RESP_CODE_OK = 200  # Success

# Algorithm return error codes --- from local
RESP_CODE_NOCERTI = 104  # Not the target certificate
RESP_CODE_NOFIND = 105  # Not found in the file
RESP_CODE_CLASMODEL = 106  # Classification model error
RESP_CODE_ALL_ERR = 400  # Unified error

# Image classification model path
MODELS_PATH = '/data/models/efficientNetV2/'

# Classification image save address
MEDIA_ROOT_FOR_ES = "/data/es/c_result/"
MEDIA_ROOT_FOR_ME = "/data/es/fig_media/"

THRESHOLD = 0.95


class efficientnetv2_Modeler:
    def __init__(self):
        self.class_indices_dict: Dict[str, Dict] = {}
        self.models_dict: Dict[str, object] = {}
        self.model_state: bool = False
        # Call the initialize_models method in __init__ to initialize the model when the object is created
        self.initialize_models()

    def initialize_models(self) -> None:
        """
        Initialize the model, try to load if the model is not loaded
        """
        if not self.model_state:
            try:
                self.class_indices_dict, self.models_dict = self.load_model_efficientNetV2()
                if self.models_dict:
                    self.model_state = True
                    logger.info("spm model loaded successfully")
                else:
                    logger.error("Model loading failed, the model dictionary is empty")
            except Exception as e:
                self.model_state = False
                logger.error(f"Error initializing and loading the model, Exception as e: {str(e)}")

    def load_model_efficientNetV2(self) -> Tuple[Dict[str, Dict], Dict[str, object]]:
        """
        Load all EfficientNetV2 models
        :return: Class index dictionary and model dictionary
        """
        try:
            tic = time.time()

            if os.path.exists(MODELS_PATH):
                for item in os.listdir(MODELS_PATH):
                    model_subpath = os.path.join(MODELS_PATH, item)
                    # Determine if item is a folder
                    if os.path.isdir(model_subpath):
                        class_indices_path = os.path.join(model_subpath, 'class_indices.json')
                        model_path = os.path.join(model_subpath, 'model.pth')

                    # Load json file
                    try:
                        with open(class_indices_path, "r") as f:
                            self.class_indices_dict[item] = json.load(f)
                        num_classes = len(self.class_indices_dict[item])
                    except FileNotFoundError:
                        logger.error(f"JSON file not found: {class_indices_path}")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON file parsing error: {str(e)}")
                    except Exception as e:
                        logger.error(f"Error loading json file: {str(e)}")

                    # Load model file
                    try:
                        model = gyl_efficientNetV2.load_model(model_path, num_classes)
                        self.models_dict[item] = model
                    except Exception as e:
                        logger.error(f"Error loading {item} model: {str(e)}")
            else:
                logger.info(f"The {MODELS_PATH} folder does not exist.")
            toc = time.time()
            logger.info(f"Time consumed to load all models: {toc - tic}s")
            return self.class_indices_dict, self.models_dict
        except Exception as e:
            logger.error(f"Error in load_model_efficientNetV2 Exception as e: {str(e)}")
            return {}, {}


def get_img_uuid(img_path: str) -> str:
    # Check input parameters
    if not img_path:
        logger.error("img_path and MEDIA_ROOT are required parameters and cannot be None or empty strings.")
        return None, None

    # Generate a unique identifier
    unique_id = str(uuid.uuid4())
    # Get file extension
    file_extension = os.path.splitext(img_path)[1].lower()
    # Build the new file name
    new_filename = f"{unique_id}{file_extension}"

    return new_filename


def fig_process_save(img_path: str, new_filename: str, MEDIA_ROOT_str: str, folder_name: str, lic_clas: str,
                     project_id: str, package_id: str, supplier_id: str, fileType: str) -> (str, str):
    """
    Save the image to the specified folder
    :param img_path: Image path, cannot be empty
    :param MEDIA_ROOT_str: Character form of MEDIA_ROOT_FOR_ME and MEDIA_ROOT_FOR_ES, cannot be empty
    :param lic_clas: Certificate category, can be empty
    :param folder_name: Folder name, can be empty
    :param project_id, package_id, supplier_id, fileType: For ES, can be empty
    :return: Saved address and unique identifier, return None and None if saving fails
    """
    # Check input parameters
    if not img_path or not new_filename:
        logger.error("img_path and new_filename are required parameters and cannot be None or empty strings.")
        return None

    if MEDIA_ROOT_str == "MEDIA_ROOT_FOR_ME":
        # Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        # Build the date folder path
        if folder_name:
            date_folder_path = os.path.join(MEDIA_ROOT_FOR_ME, current_date, folder_name)
        else:
            date_folder_path = os.path.join(MEDIA_ROOT_FOR_ME, current_date)

        # Build the final save path based on the certificate category
        folder_path = os.path.join(date_folder_path, lic_clas) if lic_clas else date_folder_path


    elif MEDIA_ROOT_str == "MEDIA_ROOT_FOR_ES":
        if not project_id or not package_id or not supplier_id or not fileType:
            logger.error(
                "project_id, package_id, supplier_id and fileType are required parameters and cannot be None or empty strings.")
            return None
        folder_path = os.path.join(MEDIA_ROOT_FOR_ES, project_id, package_id, supplier_id, fileType)
    else:
        logger.error(
            "MEDIA_ROOT_str cannot be empty and can only be the character form of MEDIA_ROOT_FOR_ME and MEDIA_ROOT_FOR_ES.")
        return None

    try:
        # Build the saved image path
        saved_img_path = os.path.join(folder_path, new_filename)

        # Create the save folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        # Copy the image to the new path
        shutil.copy2(img_path, saved_img_path)

        logger.info(f"Image saved to: {saved_img_path}")

        return folder_path  # Return the saved file name (unique identifier)

    except FileNotFoundError:
        logger.error(f"Source image file not found: {img_path}")
    except PermissionError:
        logger.error(f"Permission denied to save image to {lic_clas_figdir}")
    except Exception as e:
        logger.error(f"Unknown error occurred when saving the image: {e}")
    return None


# Instantiate the EfficientNetV2 model manager
efficientnetv2_model_manager = efficientnetv2_Modeler()
# Instantiate the OCRer for OCR recognition and fine classification
ocr_model_manager = OCR_ModelManager()


# todo: The 3-id is not saved here
def run_model_efficientnet_v2_for_one_fig(img_path: str, target_cert_list: List[str], project_id: str, package_id: str,
                                          supplier_id: str, fileType: str) -> Tuple[
    Optional[int], Optional[str], Optional[float], Optional[float], Optional[float]]:
    """
    Classify a single image using the EfficientNetV2 model
    :param img_path: Image path
    :param target_cert_list: List of target certificates
    :param efficientnetv2_model_manager: Model manager instance
    :return: Image type and probability
    """
    # todo: Initialize the model manager

    # Depending on whether unrecognized images need to be collected
    # fig_process_save(img_path, os.path.basename(img_path), "MEDIA_ROOT_FOR_ME",  "", "", "", "", "", "") # Save img_path to the date folder under MEDIA_ROOT_FOR_ME without thinking

    efficientnetv2_model_manager.initialize_models()  # The model has been loaded when instantiated earlier, can be deleted here or left to prevent previous failure to load
    ocr_model_manager.initialize_models()  # The model has been loaded when instantiated earlier, can be deleted here or left to prevent previous failure to load

    try:
        logger.info(f"Starting the classification task, run_model_efficientNetV2_forOneFig")
        tic = time.time()
        logger.info(f"img_path==={img_path}")

        img_type_en: Optional[str] = None  # Target certificate type
        img_prob: Optional[float] = None  # Target certificate probability
        saved_dir: Optional[str] = None  # Target save directory
        unique_name: Optional[str] = None  # Target certificate file name

        if ("academicCertificate" in target_cert_list) or ("degreeCertificate" in target_cert_list):
            target_cert_list.append("xuexinnet")

        for target_cert_type_i in target_cert_list:  # Only load models for target certificates

            cert_type_en, predict_prob = gyl_efficientNetV2.clas_main(
                img_path,
                efficientnetv2_model_manager.class_indices_dict[target_cert_type_i],
                efficientnetv2_model_manager.models_dict[target_cert_type_i]
            )

            logger.info(f"cert_type_en={cert_type_en}, predict_prob={predict_prob}")

            if cert_type_en:
                if cert_type_en != 'others':
                    if predict_prob > THRESHOLD:

                        doc_type_en = ocr_model_manager.ocr_class_result(img_path)  # Start OCR fine classification

                        if doc_type_en:
                            if doc_type_en in target_cert_list:
                                img_type_en = doc_type_en
                                img_prob = predict_prob
                                logging.info(
                                    f"Found the first target certificate, address: {img_path}, type: {img_type_en}, probability: {img_prob}")
                                # todo, only target certificate information is retained, do other certificates need to be saved? ? ?
                                # fig_process_save(img_path: str, MEDIA_ROOT_str:str, folder_name: str, lic_clas: str, project_id: str, package_id: str, supplier_id: str, fileType: str) -> (str):
                                img_new_name_with_uuid = get_img_uuid(img_path)
                                fig_process_save(img_path, img_new_name_with_uuid, "MEDIA_ROOT_FOR_ES", "", "",
                                                 project_id, package_id, supplier_id,
                                                 fileType)  # Save the fine classification result to the file, no longer determine if this image is other target certificate types, because it is impossible
                                saved_dir = fig_process_save(img_path, img_new_name_with_uuid, "MEDIA_ROOT_FOR_ME", "",
                                                             doc_type_en, "", "", "",
                                                             "")  # Save the fine classification result to the file, no longer determine if this image is other target certificate types, because it is impossible
                                break
                            else:
                                logger.info(
                                    f"For image {img_path}, the probability meets the threshold, but OCR fine classification is not the target certificate: lic_clas={cert_type_en}, predict_prob={predict_prob}")
                                # fig_process_save
                                break
                        else:

                            logger.info(
                                f"For image {img_path}, OCR fine classification returns None, doc_type_en={doc_type_en}, predict_prob={predict_prob}, doc_type_en={doc_type_en}")
                    else:
                        logger.info(
                            f"For image {img_path}, the probability is less than the threshold, target_cert_type_i={target_cert_type_i}, lic_clas={cert_type_en}, predict_prob={predict_prob}")
                        # fig_process_save
                else:
                    logger.info(
                        f"For image {img_path}, the classification model predicts as others, target_cert_type_i={target_cert_type_i}, lic_clas={cert_type_en}, predict_prob={predict_prob}")
                    # fig_process_save
            else:
                logger.info(
                    f"Model prediction failed, cert_type_en returns None, cert_type_en={cert_type_en}, predict_prob={predict_prob}")

        toc = time.time()
        logger.info(f"Completed classification of {img_path}, time consumed: {toc - tic}s")

        if img_type_en is None:
            logger.info(f"For image {img_path}, the model determines it is not a target certificate")
            return RESP_CODE_NOCERTI, None, None, None, None
        else:
            return RESP_CODE_OK, img_type_en, img_prob, saved_dir, img_new_name_with_uuid

    except KeyError as ke:
        logger.error(
            f"KeyError: {str(ke)}, possibly missing corresponding keys in the model dictionary or index dictionary.")
    except Exception as e:
        logger.error(f"in run_model_efficientnet_v2_for_one_fig Exception as e: {str(e)}")

    return RESP_CODE_ALL_ERR, None, None, None, None