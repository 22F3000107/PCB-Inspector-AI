
from pathlib import Path

import cv2
import numpy as np


def load_image(image_path):
    """
    Load an image from disk in OpenCV BGR format.
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    return image


def validate_image(image):
    """
    Validate an image represented as a NumPy array.
    """

    if not isinstance(image, np.ndarray):
        raise TypeError("Image must be a NumPy array.")

    if image.size == 0:
        raise ValueError("Image is empty.")

    if image.ndim not in (2, 3):
        raise ValueError("Unsupported image dimensions.")

    if image.ndim == 3 and image.shape[2] not in (3, 4):
        raise ValueError("Expected a 3-channel or 4-channel image.")

    return image


def to_grayscale(image):
    """
    Convert an image to grayscale.
    """

    validate_image(image)

    if image.ndim == 2:
        return image

    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)

    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def preprocess_for_alignment(image):
    """
    Prepare an image for feature detection and matching.

    CLAHE improves local contrast.
    A small Gaussian blur reduces high-frequency noise.
    """

    gray = to_grayscale(image)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    enhanced = clahe.apply(gray)

    processed = cv2.GaussianBlur(
        enhanced,
        (3, 3),
        0,
    )

    return processed
