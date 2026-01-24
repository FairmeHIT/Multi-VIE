import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
import tempfile
import logging
import sys
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

from os.path import dirname, abspath

# Add the parent directory to sys.path
sys.path.append(dirname(dirname(abspath(__file__))))


def preprocess_image_for_ocr(img_path, output_path=None, denoise=True, remove_bg=True, enhance_contrast=True,
                             resize=True, thresholding=True, blur=True, replace_original=False,
                             threshold_type='adaptive', debug=False):
    """
    Preprocess an image to improve OCR recognition accuracy

    Args:
        img_path: Path to the input image
        output_path: Optional output image path, default is None (don't save)
        denoise: Whether to apply noise reduction
        remove_bg: Whether to attempt background removal
        enhance_contrast: Whether to enhance contrast
        resize: Whether to resize the image
        thresholding: Whether to apply thresholding
        blur: Whether to apply blurring
        replace_original: Whether to replace the original image
        threshold_type: Threshold type ('adaptive' or 'otsu')
        debug: Whether to print debug information

    Returns:
        Preprocessed image array
    """
    try:
        # Read the image
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"Failed to read image: {img_path}")

        if debug:
            logger.info(f"Original image shape: {img.shape}, type: {img.dtype}")
            logger.info(f"Pixel value range: min={np.min(img)}, max={np.max(img)}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Resize the image to improve OCR accuracy
        if resize:
            gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

        # Noise reduction
        if denoise:
            gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            if debug: logger.info("Applied noise reduction")

        # Blur processing
        if blur:
            gray = cv2.medianBlur(gray, 3)
            if debug: logger.info("Applied blurring")

        # Thresholding
        if thresholding:
            if threshold_type == 'adaptive':
                # Adaptive thresholding works better for uneven lighting
                gray = cv2.adaptiveThreshold(
                    gray, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY, 11, 2
                )
                if debug: logger.info("Applied adaptive thresholding")
            else:
                # Otsu's binarization
                _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                if debug: logger.info("Applied Otsu's binarization")

        # Background removal
        if remove_bg:
            try:
                # Create a mask and apply GrabCut algorithm
                mask = np.zeros(gray.shape[:2], np.uint8)
                bgdModel = np.zeros((1, 65), np.float64)
                fgdModel = np.zeros((1, 65), np.float64)
                rect = (10, 10, gray.shape[1] - 20, gray.shape[0] - 20)
                cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
                mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
                gray = gray * mask2
                if debug: logger.info("Applied background removal")
            except Exception as e:
                logger.info(f"Background removal failed: {e}")

        # Contrast enhancement
        if enhance_contrast:
            # Check if the image is completely black
            if np.max(gray) == 0:
                logger.info("Warning: Image is already completely black, skipping contrast enhancement")
            else:
                pil_img = Image.fromarray(gray)
                enhancer = ImageEnhance.Contrast(pil_img)
                pil_img = enhancer.enhance(2.0)
                gray = np.array(pil_img)
                if debug: logger.info("Applied contrast enhancement")

        if debug:
            logger.info(f"Processed pixel value range: min={np.min(gray)}, max={np.max(gray)}")
            if np.max(gray) == 0:
                logger.info("Warning: Processed image is completely black!")

        # Save the result
        if output_path:
            cv2.imwrite(output_path, gray)

        # Replace the original image
        if replace_original:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(img_path)[1])
            temp_path = temp_file.name
            temp_file.close()

            cv2.imwrite(temp_path, gray)
            os.replace(temp_path, img_path)
            logger.info(f"Replaced original image: {img_path}")

        return gray

    except Exception as e:
        logger.info(f"Error during image processing: {e}")
        return None

