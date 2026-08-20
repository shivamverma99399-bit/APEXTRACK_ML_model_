from pathlib import Path
from typing import Optional, Tuple, Any
from app.core.config import settings
from app.core.exceptions import ModelLoadException, ModelNotConfiguredException
from app.core.logging import logger

try:
    from transformers import AutoImageProcessor, AutoModelForImageClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class HFModelLoader:
    """
    Singleton cached loader for Hugging Face image classification models and processors.
    """

    _cached_model: Optional[Any] = None
    _cached_processor: Optional[Any] = None
    _cached_target: Optional[str] = None

    @classmethod
    def get_configured_model_target(cls) -> Optional[str]:
        """
        Determines target model identifier prioritizing:
        1. HF_MODEL_ID
        2. MODEL_ID
        3. MODEL_PATH (with relative local fallback resolution)
        """
        if settings.HF_MODEL_ID:
            return settings.HF_MODEL_ID
        if settings.MODEL_ID:
            return settings.MODEL_ID
        if settings.MODEL_PATH:
            return settings.MODEL_PATH

        # Local development auto-discovery fallbacks
        candidate_paths = [
            Path("models/apextrack-vit-v2"),
            Path("../ml/models/apextrack-vit-v2"),
            Path("ml/models/apextrack-vit-v2"),
        ]
        for p in candidate_paths:
            if p.exists() and (p / "model.safetensors").exists():
                return str(p)

        return None

    @classmethod
    def is_configured(cls) -> bool:
        """
        Returns True if a valid model identifier or local model path is resolved.
        """
        return bool(cls.get_configured_model_target())

    @classmethod
    def load_model_and_processor(
        cls,
        model_id_or_path: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Tuple[Any, Any]:
        """
        Loads and caches Hugging Face model and image processor.
        """
        target = model_id_or_path or cls.get_configured_model_target()
        auth_token = token or settings.HF_TOKEN

        if not target:
            raise ModelNotConfiguredException(
                "No Hugging Face model ID or valid local model path specified in configuration."
            )

        if not TRANSFORMERS_AVAILABLE:
            raise ModelLoadException(
                "The 'transformers' or 'torch' package is not available in the Python runtime environment."
            )

        # Return cached instance if target hasn't changed
        if cls._cached_model is not None and cls._cached_processor is not None and cls._cached_target == target:
            return cls._cached_model, cls._cached_processor

        try:
            logger.info(f"Loading Hugging Face image processor from: {target}")
            processor = AutoImageProcessor.from_pretrained(
                target,
                token=auth_token,
            )

            logger.info(f"Loading Hugging Face image classification model from: {target}")
            model = AutoModelForImageClassification.from_pretrained(
                target,
                token=auth_token,
            )

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model.to(device)
            model.eval()

            # Store in cache
            cls._cached_model = model
            cls._cached_processor = processor
            cls._cached_target = target

            logger.info(f"Hugging Face model successfully loaded and cached on device: {device}")
            return model, processor
        except Exception as e:
            logger.error(f"Failed to load Hugging Face model '{target}': {str(e)}", exc_info=True)
            raise ModelLoadException(
                f"Failed to load Hugging Face model '{target}': {str(e)}"
            )
