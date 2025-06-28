import os
import time
from typing import Tuple, Union
from shutil import copy2, move
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# Maximum number of loops, can be adjusted according to actual situation
MAX_LOOP_TIMES = 10
# Minimum file size threshold in bytes, set to 10KB here
MIN_FILE_SIZE = 10240
# Maximum file size threshold, 2MB
MAX_FILE_SIZE = 2 * 1024 * 1024

# Define status codes for this module
DATA_CODE_OK = 200
DATA_CODE_ALL_ERR = 400


def save_image(image: Image.Image, output_path: str, quality: int) -> None:
    """
    Universal function to save images, processes according to image format
    :param image: PIL Image object
    :param output_path: Output file path
    :param quality: Image save quality
    """
    if image.format == "PNG":
        # If it's a PNG format, first convert to RGB mode (JPEG doesn't support transparency channel), then save as JPEG
        rgb_image = image.convert("RGB")
        rgb_image.save(output_path, optimize=True, quality=quality, format="JPEG")
    else:
        image.save(output_path, optimize=True, quality=quality)


def process_image_size(input_path: str) -> Tuple[Union[bool, None], Union[str, None], int]:
    """
    Process image size, adjust according to file size
    :param input_path: Input image file path
    :return: Processing result tuple (whether processing succeeded, processed file path, status code)
    """
    backup_file = None

    try:
        tic = time.time()
        # Check if file exists
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"File {input_path} does not exist")

        # Get file size
        file_size = os.path.getsize(input_path)

        if file_size < MIN_FILE_SIZE:
            # File size is smaller than minimum threshold, do not adjust size
            toc = time.time()
            logger.info(
                f"Input file {input_path} is smaller than 10kb, image size not adjusted, time consumed: {toc - tic}s")
            return False, input_path, DATA_CODE_OK
        elif file_size > MAX_FILE_SIZE:
            # Create temporary backup file
            dir_name = os.path.dirname(input_path)
            file_name = os.path.basename(input_path)
            backup_file = os.path.join(dir_name, f".{file_name}.bak")

            # Backup original file
            copy2(input_path, backup_file)

            # Open image file
            image = Image.open(input_path)

            quality = 100  # Initial quality set to 100
            loop_count = 0  # Record loop count

            while file_size > MAX_FILE_SIZE and loop_count < MAX_LOOP_TIMES:
                quality -= 10  # Decrease quality by 10 each time
                if quality < 0:
                    quality = 0

                # Save directly to original path
                save_image(image, input_path, quality)
                file_size = os.path.getsize(input_path)
                loop_count += 1

            # Close image file
            image.close()

            # Delete backup file
            if backup_file and os.path.exists(backup_file):
                os.remove(backup_file)

            toc = time.time()
            logger.info(
                f"Input file {input_path} has been compressed, new file size: {file_size} bytes, time consumed: {toc - tic}s")
            return True, input_path, DATA_CODE_OK
        else:
            # File size is within appropriate range, no need to adjust size
            toc = time.time()
            logger.info(f"Input file {input_path} image size does not need adjustment, time consumed: {toc - tic}s")
            return True, input_path, DATA_CODE_OK

    except FileNotFoundError as e:
        logger.error(str(e))
        return None, None, DATA_CODE_ALL_ERR
    except PermissionError:
        logger.error(f"Permission denied to access file {input_path}")
        return None, None, DATA_CODE_ALL_ERR
    except Exception as e:
        logger.error(f"An unknown error occurred while processing file {input_path}: {str(e)}")
        return None, None, DATA_CODE_ALL_ERR
    finally:
        # If processing failed and backup file exists, restore original file
        if backup_file and os.path.exists(backup_file):
            try:
                # Ensure original file has been deleted or does not exist
                if os.path.exists(input_path):
                    os.remove(input_path)
                move(backup_file, input_path)
                logger.warning(f"Image compression failed, original file {input_path} has been restored")
            except Exception as e:
                logger.error(f"Failed to restore original file: {str(e)}")