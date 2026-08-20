from typing import Tuple
from fastapi import UploadFile
from PIL import Image
from app.core.exceptions import InvalidImageException
from app.core.logging import logger
from app.utils.file_validation import validate_image_file


class ImageService:
    """
    Service for uploading, validating, and extracting metadata from uploaded track images.
    """

    async def process_upload(self, file: UploadFile) -> Tuple[Image.Image, dict]:
        """
        Reads raw bytes from UploadFile, validates image contents, and returns PIL Image with metadata.

        Args:
            file (UploadFile): Uploaded multipart form file.

        Returns:
            Tuple[Image.Image, dict]: Decoded PIL Image and metadata.
        """
        if not file:
            raise InvalidImageException("No file payload was provided.")

        logger.info(f"Processing image upload: filename='{file.filename}', content_type='{file.content_type}'")

        try:
            content = await file.read()
        except Exception as e:
            logger.error(f"Error reading file bytes from upload: {str(e)}")
            raise InvalidImageException("Failed to read uploaded file data.")

        pil_image, metadata = validate_image_file(
            content=content,
            content_type=file.content_type or "",
        )

        metadata["original_filename"] = file.filename or "unknown"
        logger.info(
            f"Image successfully validated: format={metadata['format']}, "
            f"dimensions={metadata['width']}x{metadata['height']}, size={metadata['size_bytes']} bytes"
        )
        return pil_image, metadata
