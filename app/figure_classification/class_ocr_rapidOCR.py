import time
from rapidocr_paddle import RapidOCR
from paddleocr import PaddleOCR
import paddle
import logging
import sys
import os
from typing import Optional, Dict, List, Tuple
logger = logging.getLogger(__name__)


from os.path import dirname, abspath
# Add the parent directory to sys.path
sys.path.append(dirname(dirname(abspath(__file__))))

# from data_process import data_predefined
from app.data_process import data_predefined

# Configuration information
MODEL_PATH = "/data/models/paddleocr"

# Test version uses incoming parameters
# MAX_MATCHES = 5


class OCR_ModelManager:
    def __init__(self):
        self.model_state_ocr: bool = False
        self.initialize_models()

    def initialize_models(self) -> None:
        if not self.model_state_ocr:
            try:
                self.ocr = RapidOCR(det_use_cuda=True, cls_use_cuda=True, rec_use_cuda=True)
                logger.info("RapidOCR model initialized successfully.")
                self.model_state_ocr = True
            except Exception as e:
                self.model_state_ocr = False
                logger.error(f"Failed to initialize PaddleOCR model, error message: {e}")

    def ocr_fig(self, image_path: str) -> Optional[str]:
        '''
        Perform OCR recognition on the image at the given path
        :param image_path: Path to the image to be recognized
        :return: Recognized text content
        '''
        # Check if the image path and model path are empty
        if not image_path:
            logger.error(f"The image path cannot be empty, image path: {image_path}")
            return None
        # Check if the image file exists
        if not os.path.isfile(image_path):
            logger.error(f"The image file does not exist, image path: {image_path}")
            return None

        try:
            # Perform OCR recognition
            start_time = time.time()
            result, elapse_list = self.ocr(image_path)

            toc = time.time()
            text = ""
            for res in result:
                text = text + res[1]

            # logger.info(f"OCR recognition result: {text}")
            end_time = time.time()
            logger.info(f"OCR execution time for image {image_path}: {end_time - start_time} seconds")
            return text
        except Exception as e:
            logger.error(f"Error occurred while processing image {image_path} with OCR: {e}")
        return None

    def determine_lic_type(self, text: str, MAX_MATCHES: int) -> Tuple[str, int]:
        """
        Determine the certificate type and corresponding number based on the extracted text
        :param text: Text content recognized by OCR
        :return: Tuple of certificate type and corresponding number
        """
        # Check if the text is empty
        if not text:
            logger.error(f"The text content is empty, unable to determine certificate type, text content: {text}")
            return '', 0

        start_time = time.time()
        document_type = ''
        max_matches = 0

        # Define keywords for determining license type
        keywords = data_predefined.fig_class_keywords
        # Check if the keywords list is empty
        if not keywords:
            logger.error(f"The keyword list is empty, unable to determine certificate type, keyword list: {keywords}")
            return '', 0

        for doc_type, keyword_list in keywords.items():
            matches = sum(keyword in text for keyword in keyword_list)
            # logger.info(f"matches=={matches}")
            if matches >= max_matches and matches >= MAX_MATCHES:
                max_matches = matches
                document_type = doc_type

        end_time = time.time()
        logger.info(f"max_matches:{max_matches}")
        # logger.info(f"Execution time for determining certificate type: {end_time - start_time} seconds")

        return document_type, max_matches

    def ocr_class_result(self, img_path: str, MAX_MATCHES: int) -> Optional[str]:
        ocr_text = self.ocr_fig(img_path)
        logger.info(f"ocr_text: {ocr_text}")

        cert_type_en = ''
        if ocr_text:
            # Determine certificate type based on recognition result
            cert_type_en, max_matches = self.determine_lic_type(ocr_text, MAX_MATCHES)
            logger.info(f"The OCR classification result for image {img_path} is: {cert_type_en}")

            if cert_type_en:
                return cert_type_en
            else:
                logger.info(f"The classification result for image {img_path} is empty")
                return None
        else:
            logger.error(f"The OCR recognition result for image {img_path} is empty")
            return None