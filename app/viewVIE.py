"""
Author: Huafu Li
Date: 2025-06-26
Description: API service for certificate image classification and information extraction.
"""

import logging
import time
import os
import sys
import uuid
import datetime
from typing import List, Dict, Tuple, Union, Optional
import json
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor
from rest_framework.decorators import api_view
from rest_framework.response import Response
import fitz  # PyMuPDF

# Configure logging
logger = logging.getLogger(__name__)

MEDIA_ROOT = "/data"
os.makedirs(MEDIA_ROOT, exist_ok=True)

from app import process
from app.data_process.data_predefined import target_type_list_en, target_type_num_mapping_en
from app.llm import main_fig_VIE


def response_body(status_code: int, message: str, data: Optional[Union[Dict, List]]) -> Dict:
    """Construct a unified response body format"""
    return {
        'status': status_code,
        'message': message,
        'data': data
    }


def delete_file_async(file_path: str) -> None:
    """Asynchronously delete a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file: {e}")


def delete_directory_async(dir_path: str) -> None:
    """Asynchronously delete a directory"""
    try:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            logger.info(f"Directory deleted: {dir_path}")
    except Exception as e:
        logger.error(f"Error deleting directory: {e}")


def extract_images_from_pdf_all(pdf_path: str) -> Tuple[int, List[str]]:
    """
    Extract all images from a PDF file

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Tuple containing the number of images and a list of image paths
    """
    logger.info(f"Starting to extract all images from PDF file {pdf_path}")
    pdf = fitz.open(pdf_path)
    image_count = 0
    image_paths = []  # Array to store image paths

    # Get the directory and base name (without extension) of the PDF file for creating the folder name
    pdf_dir = os.path.dirname(pdf_path)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_folder = pdf_dir
    logger.info(f"PDF folder: {output_folder}")

    try:
        # Get disk usage information for the output folder
        st = os.statvfs(output_folder)
        free_space_bytes = st.f_bavail * st.f_frsize
        free_space_mb = free_space_bytes / (1024 * 1024)  # Convert bytes to MB
        logger.info(f"Available space in output folder: {free_space_mb} MB")

        # Get the size of the PDF file
        pdf_size_bytes = os.path.getsize(pdf_path)
        pdf_size_mb = pdf_size_bytes / (1024 * 1024)  # Convert bytes to MB
        logger.info(f"Size of PDF file: {pdf_size_mb} MB")

        for page in pdf:
            image_count += len(page.get_images(full=True))
            for img_index, img in enumerate(page.get_images(full=True), start=1):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image_filename = f"{pdf_name}_page{page.number + 1}_img{img_index}.png"
                image_path = os.path.join(output_folder, image_filename)
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)
                image_paths.append(image_path)

        logger.info(f"Extracted {image_count} images from {pdf_path}")
        logger.info(f"Image paths: {image_paths}")
        return image_count, image_paths
    except Exception as e:
        logger.error(f"Exception in extract_images_from: {str(e)}, pdf_path={pdf_path}, output_folder={output_folder}")
        return 0, []
    finally:
        pdf.close()


def classify_image_internal(image_path: str, target_cert_list: List[str], process_type: str, THRESHOLD_level1: float,
                            THRESHOLD_level2: float, THRESHOLD: float, MAX_MATCHES: int, enhance_img: bool) -> Dict:
    """
    Internal image classification function, does not directly handle HTTP requests

    Args:
        image_path: Path to the image
        target_cert_list: List of target certificates
        actual_type: Actual type

    Returns:
        Dictionary containing classification results
    """
    try:
        logger.info(f"Starting to process image: {image_path}")

        # Check and preprocess the image
        valid_fig_list, invalid_fig_list = process.check_input_fig_and_preprocess([image_path])

        # If the image is invalid, log an error and return
        if not valid_fig_list:
            logger.error(f"Invalid image: {os.path.basename(image_path)}")
            return {
                "image_name": os.path.basename(image_path),
                "status": "error",
                "message": "Invalid image, please check if the image is normal"
            }

        # Classify the image using the model
        tic = time.time()
        img_info_list = process.class_fig_list_using_efficientNetV2(valid_fig_list, target_cert_list, process_type,
                                                                      THRESHOLD_level1, THRESHOLD_level2, THRESHOLD,
                                                                      MAX_MATCHES, enhance_img)
        toc = time.time()
        logger.info(f"img_info_list: {img_info_list}")
        logger.info(f"Prediction time: {toc - tic:.2f}s")

        # Check the classification results
        if not img_info_list:
            logger.error(f"Empty classification results for image: {os.path.basename(image_path)}")
            return {
                "image_name": os.path.basename(image_path),
                "predicted_type": None,
                "message": "Empty classification results, please check if the image is a target image"
            }

        # Extract the classification results
        cert_type_en_rec = img_info_list[0]['cert_type_en']
        predict_prob = img_info_list[0]['predict_prob']
        logger.info(f"Prediction probability for image {img_info_list[0]['img_path']}: {predict_prob}")

        # Generate the classification result
        return {
            'image_name': os.path.basename(image_path),
            'predicted_type': cert_type_en_rec,
            'predict_probability': predict_prob,
        }

    except Exception as e:
        logger.error(f"Error classifying image: {os.path.basename(image_path)}, Error: {str(e)}")
        return {
            "image_name": os.path.basename(image_path),
            "status": "error",
            "message": str(e)
        }


def getVIE(img_path, cert_type_en):
    # Call LLM to get VIE results
    result, llm_resp_code = main_fig_VIE.call_llm_interface(img_path, cert_type_en)
    result.pop("resp_code", None)
    result.pop("resp_msg", None)
    result["type"] = target_type_num_mapping_en[result["type"]]
    logger.info(f"result: {result}")

    return result


@api_view(['POST'])
def classifyImageThenVIE(request):
    """Process uploaded files (PDF or images) and perform classification"""
    try:
        # Get the uploaded file
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(response_body(400, "File missing from request", None), status=400)

        # Get optional parameters
        data = request.data
        target_cert_list = data.get("targetCertList", target_type_list_en)
        process_type = data.get("process_type", "oneModel")
        THRESHOLD_level1 = float(data.get("THRESHOLD_level1", 0.99))
        THRESHOLD_level2 = float(data.get("THRESHOLD_level2", 0.60))
        THRESHOLD = float(data.get("THRESHOLD", 0.90))
        MAX_MATCHES = int(data.get("MAX_MATCHES", 5))
        enhance_img = bool(data.get("enhance_img", False))

        if isinstance(target_cert_list, str):  # If the list is a string
            try:
                target_cert_list = json.loads(target_cert_list)
            except json.JSONDecodeError:
                target_cert_list = target_cert_list.split(',') if target_cert_list else []

        # Create a temporary directory
        temp_dir = os.path.join(MEDIA_ROOT, 'temp_uploads', str(uuid.uuid4()))
        os.makedirs(temp_dir, exist_ok=True)

        # Save the uploaded file - use the original filename (safely processed)
        file_ext = os.path.splitext(file_obj.name)[1].lower()
        # Safe processing: Only keep the filename part to prevent path traversal attacks
        safe_filename = os.path.basename(file_obj.name)
        temp_file_path = os.path.join(temp_dir, safe_filename)

        with open(temp_file_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        if file_ext == '.pdf':
            # Process PDF file
            logger.info(f"Received PDF file, starting to extract images: {temp_file_path}")
            image_count, image_paths = extract_images_from_pdf_all(temp_file_path)

            if not image_paths:
                return Response(
                    response_body(400, "Failed to extract images from PDF, check if PDF contains images", None),
                    status=400)

            logger.info(f"Successfully extracted {image_count} images from PDF")
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            # Process image file
            image_paths = [temp_file_path]
        else:
            return Response(
                response_body(400, "Unsupported file type, only .pdf, .jpg, .jpeg, .png are supported", None),
                status=400)

        # Process images
        results = []
        for image_path in image_paths:
            # Call the image classification function
            result = classify_image_internal(image_path, target_cert_list, process_type, THRESHOLD_level1,
                                             THRESHOLD_level2, THRESHOLD, MAX_MATCHES, enhance_img)

            if result["predicted_type"] and result["predicted_type"] in target_cert_list:
                result = getVIE(image_path, result["predicted_type"])
                results.append(result)

        # Asynchronously delete the temporary directory
        threading.Thread(target=delete_directory_async, args=(temp_dir,)).start()

        return Response(response_body(200, "File processed successfully", {"results": results}), status=200)

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return Response(response_body(500, f"Internal server error: {str(e)}", None), status=500)