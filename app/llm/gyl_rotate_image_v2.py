import cv2
import paddleclas
import time
import logging
import numpy as np
import os
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class ImageOrientationRotator:
    def __init__(self):
        """
        Initialize the image orientation predictor
        """
        try:
            self.image_orientation_predictor = paddleclas.PaddleClas(
                model_name="text_image_orientation"
            )
        except Exception as e:
            logger.error(f"Failed to initialize image orientation predictor: {e}")

    def rotate_image_by_orientation(self, img_path):
        """
        Rotate the image based on the predicted orientation and return the path of the rotated image

        Args:
            img_path (str): Path to the image to be processed

        Returns:
            rotated_img_path (str or None): Path to the rotated image, or None if an error occurs
        """
        try:
            img_dir = os.path.dirname(img_path)
            tic = time.time()

            # Predict image orientation
            cls_result = self.image_orientation_predictor.predict(input_data=img_path)
            cls_res = next(cls_result)

            angle = cls_res[0]['label_names'][0]
            logger.info(f"Predicted rotation angle: {angle}")

            cv_rotate_code = {
                '90': cv2.ROTATE_90_COUNTERCLOCKWISE,
                '180': cv2.ROTATE_180,
                '270': cv2.ROTATE_90_CLOCKWISE
            }

            if angle in cv_rotate_code:
                logger.info(f"Image angle: {angle}, applying rotation code: {cv_rotate_code[angle]}")
                img_np = cv2.imread(img_path)

                rotated_img = cv2.rotate(img_np, cv_rotate_code[angle])

                # Construct new filename
                img_filename = os.path.basename(img_path)
                rotated_img_filename = "rotated_" + img_filename
                rotated_img_path = os.path.join(img_dir, rotated_img_filename)

                # Save rotated image
                cv2.imwrite(rotated_img_path, rotated_img)

                toc = time.time()
                logger.info(f"Image rotation completed in {toc-tic:.4f} seconds")
                return rotated_img_path
            else:
                logger.info(f"No rotation needed: {angle}")
                return None
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            return None
        except KeyError as e:
            logger.error(f"Key error: {e}")
            return None
        except cv2.error as e:
            logger.error(f"OpenCV error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None