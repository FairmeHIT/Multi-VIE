import sys
import os
import json
import time
import torch
from PIL import Image
from torchvision import transforms
import logging

from typing import Optional, Dict, List, Tuple
from app.figure_classification.code.efficientNetV2.models_train.model import efficientnetv2_m as create_model

logger = logging.getLogger(__name__)

# Constants
IMG_SIZE = {"s": [300, 384], "m": [384, 480], "l": [384, 480]}
MODEL_TYPE = "m"
NORMALIZE_MEAN = [0.5, 0.5, 0.5]
NORMALIZE_STD = [0.5, 0.5, 0.5]


def get_device() -> torch.device:
    """Get available device (GPU/CPU)"""
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    return device


def load_model(model_weight_path: str, num_classes: int) -> Optional[torch.nn.Module]:
    """
    Load classification model and set to evaluation mode

    Args:
        model_weight_path: Path to model weights
        num_classes: Number of classification categories

    Returns:
        Loaded model or None on error
    """
    device = get_device()
    try:
        model = create_model(num_classes).to(device)
        logger.info(f"Loading model from: {model_weight_path}")
        model.load_state_dict(torch.load(model_weight_path, map_location=device))
        model.eval()
        logger.info(f"Model loaded successfully")
        return model
    except FileNotFoundError:
        logger.error(f"Model file not found: {model_weight_path}")
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
    return None


def combined_resize_crop(img: Image.Image, size: int) -> Image.Image:
    """
    Resize and center crop image

    Args:
        img: Input image
        size: Target size

    Returns:
        Processed image
    """
    img = transforms.functional.resize(img, size)
    img = transforms.functional.center_crop(img, size)
    return img


def preprocess_image(img_path: str, target_size: int) -> Optional[torch.Tensor]:
    """
    Preprocess image for model input

    Args:
        img_path: Path to image
        target_size: Target size for resize/crop

    Returns:
        Preprocessed image tensor or None on error
    """
    try:
        img = Image.open(img_path).convert('RGB')
        img = combined_resize_crop(img, target_size)
        img = transforms.functional.to_tensor(img)
        img = transforms.functional.normalize(img, NORMALIZE_MEAN, NORMALIZE_STD)
        return img
    except FileNotFoundError:
        logger.error(f"Image not found: {img_path}")
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
    return None


def clas_main(img_path: str, class_indict: Dict[str, str], model: torch.nn.Module) -> Tuple[
    Optional[str], Optional[float]]:
    """
    Classify image and return result with probability

    Args:
        img_path: Path to image
        class_indict: Class index dictionary
        model: Trained classification model

    Returns:
        Tuple of class name and probability, or (None, None) on error
    """
    start_time = time.time()

    if not class_indict:
        logger.info(f"Empty class dictionary for image: {img_path}")
        return None, None

    device = get_device()

    try:
        target_size = IMG_SIZE[MODEL_TYPE][1]
        img = preprocess_image(img_path, target_size)

        if img is None:
            return None, None

        img = torch.unsqueeze(img, dim=0)

        with torch.no_grad():
            output = torch.squeeze(model(img.to(device))).cpu()
            predict = torch.softmax(output, dim=0)
            class_idx = torch.argmax(predict).item()

        probability = predict[class_idx].item()
        class_name = class_indict[str(class_idx)]

        end_time = time.time()
        logger.info(
            f"Image {img_path} classified as: {class_name}, Probability: {probability:.4f}, Time: {end_time - start_time:.2f}s")

        return class_name, probability

    except Exception as e:
        logger.error(f"Error during classification: {str(e)}")

    return None, None


if __name__ == '__main__':
    device = get_device()
    print(f"Device: {device}")

    # Load class indices
    json_path = './class_indices.json'
    assert os.path.exists(json_path), f"Class indices file not found: {json_path}"

    with open(json_path, "r") as f:
        class_indict = json.load(f)

    # Load model
    start_time = time.time()
    model = load_model("/path/to/model_weights.pth", len(class_indict))
    end_time = time.time()
    print(f"Model loaded in {end_time - start_time:.2f}s")

    # Test images
    test_images = []

    # Run classification
    total_time = 0
    for img_path in test_images:
        start_time = time.time()
        class_name, prob = clas_main(img_path, class_indict, model)
        end_time = time.time()
        total_time += end_time - start_time
        print(f"Image: {os.path.basename(img_path)} -> Class: {class_name}, Prob: {prob:.4f}")

    print(f"Total classification time: {total_time:.2f}s")