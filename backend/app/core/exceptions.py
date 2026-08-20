from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class ApexTrackException(Exception):
    """
    Base exception for ApexTrack AI application errors.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code


class EmptyFileException(ApexTrackException):
    def __init__(self, message: str = "The uploaded file is empty."):
        super().__init__(
            message=message,
            error_code="EMPTY_FILE",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidImageException(ApexTrackException):
    def __init__(self, message: str = "The uploaded file is not a valid image."):
        super().__init__(
            message=message,
            error_code="INVALID_IMAGE",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UnsupportedImageTypeException(ApexTrackException):
    def __init__(
        self,
        message: str = "The uploaded image format is not supported.",
    ):
        super().__init__(
            message=message,
            error_code="UNSUPPORTED_IMAGE_TYPE",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


class ImageTooLargeException(ApexTrackException):
    def __init__(
        self,
        message: str = "The uploaded file size exceeds the allowed limit.",
    ):
        super().__init__(
            message=message,
            error_code="IMAGE_TOO_LARGE",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )


class ModelNotConfiguredException(ApexTrackException):
    def __init__(
        self,
        message: str = "Hugging Face model is not configured. Real inference will be enabled in the ML phase.",
    ):
        super().__init__(
            message=message,
            error_code="MODEL_NOT_CONFIGURED",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class ModelLoadException(ApexTrackException):
    def __init__(
        self,
        message: str = "Failed to load the configured ML model.",
    ):
        super().__init__(
            message=message,
            error_code="MODEL_LOAD_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class InferenceException(ApexTrackException):
    def __init__(
        self,
        message: str = "An error occurred during model inference.",
    ):
        super().__init__(
            message=message,
            error_code="INFERENCE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def apextrack_exception_handler(
    request: Request, exc: ApexTrackException
) -> JSONResponse:
    """
    Global exception handler for custom ApexTrack exceptions.
    Returns standardized error response schema.
    """
    logger.warning(
        f"API Error [{exc.error_code}] at {request.url.path}: {exc.message}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            }
        },
    )


async def global_unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Catch-all handler for unhandled server exceptions to prevent leaking stack traces.
    """
    logger.error(
        f"Unhandled Server Error at {request.url.path}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred.",
            }
        },
    )
