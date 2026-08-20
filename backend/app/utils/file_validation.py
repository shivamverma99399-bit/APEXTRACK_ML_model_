import io
from typing import Tuple
import cv2
import numpy as np
from PIL import Image, ImageOps
from app.core.config import settings
from app.core.exceptions import (
    EmptyFileException,
    ImageTooLargeException,
    InvalidImageException,
    UnsupportedImageTypeException,
)
from app.core.logging import logger


def validate_image_file(content: bytes, content_type: str = "") -> Tuple[Image.Image, dict]:
    """
    Validates uploaded image file bytes.

    Validation checks performed:
    1. File is non-empty.
    2. File size is within MAX_IMAGE_SIZE_MB.
    3. Content type / MIME type is acceptable if supplied.
    4. Image is readable and non-corrupted via Pillow.
    5. Image can be decoded into NumPy array via OpenCV.
    6. Image dimensions (width, height) are positive.

    Returns:
        Tuple[Image.Image, dict]: A valid, converted RGB PIL Image and metadata dict (width, height, format).
    """
    if not content or len(content) == 0:
        logger.warning("File validation failed: File is empty.")
        raise EmptyFileException()

    content_size = len(content)
    if content_size > settings.max_image_size_bytes:
        logger.warning(
            f"File validation failed: Size ({content_size} bytes) exceeds limit ({settings.max_image_size_bytes} bytes)."
        )
        raise ImageTooLargeException(
            f"Image size ({content_size / (1024*1024):.2f} MB) exceeds maximum allowed limit of {settings.MAX_IMAGE_SIZE_MB} MB."
        )

    # Optional preliminary content-type check
    if content_type:
        clean_content_type = content_type.lower().split(";")[0].strip()
        if clean_content_type and clean_content_type not in settings.ALLOWED_MIME_TYPES:
            logger.warning(f"File validation failed: MIME type '{clean_content_type}' not allowed.")
            raise UnsupportedImageTypeException(
                f"Content type '{clean_content_type}' is not supported. Allowed formats: JPEG, PNG, WEBP."
            )

    # Pillow deep readability & format verification
    try:
        image_stream = io.BytesIO(content)
        pil_img = Image.open(image_stream)
        pil_format = pil_img.format  # e.g., 'JPEG', 'PNG', 'WEBP'
        
        # Ensure image metadata can be loaded
        pil_img.load()
    except Exception as e:
        logger.warning(f"Pillow image decoding failed: {str(e)}")
        raise InvalidImageException("The uploaded file could not be decoded as a valid image.")

    if not pil_format or pil_format.upper() not in ["JPEG", "MPO", "PNG", "WEBP", "JPG"]:
        logger.warning(f"File validation failed: Unrecognized or unsupported image format '{pil_format}'.")
        raise UnsupportedImageTypeException(
            f"Image format '{pil_format}' is not supported. Allowed formats: JPEG, PNG, WEBP."
        )

    width, height = pil_img.size
    if width <= 0 or height <= 0:
        logger.warning(f"File validation failed: Invalid dimensions ({width}x{height}).")
        raise InvalidImageException(f"Invalid image dimensions: {width}x{height}.")

    # OpenCV decoding verification
    try:
        np_arr = np.frombuffer(content, np.uint8)
        cv_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if cv_img is None or cv_img.size == 0:
            logger.warning("OpenCV imdecode failed to read image buffer.")
            raise InvalidImageException("Image buffer is corrupted or invalid for computer vision processing.")
    except Exception as e:
        if isinstance(e, InvalidImageException):
            raise
        logger.warning(f"OpenCV processing exception: {str(e)}")
        raise InvalidImageException("Image buffer cannot be processed by computer vision decoder.")

    # Orient properly according to EXIF if applicable, and convert to RGB
    pil_img = ImageOps.exif_transpose(pil_img)
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    metadata = {
        "width": width,
        "height": height,
        "format": pil_format.upper(),
        "size_bytes": content_size,
    }

    return pil_img, metadata
