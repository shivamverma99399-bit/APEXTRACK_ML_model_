from typing import Any, Optional
from PIL import Image
import torch


class ImagePreprocessor:
    """
    Image preprocessing pipeline.
    Handles image formatting, size normalization, and delegation to Hugging Face processors when available.
    """

    def __init__(self, hf_processor: Optional[Any] = None, target_size: tuple = (224, 224)):
        self.hf_processor = hf_processor
        self.target_size = target_size

    def preprocess(self, image: Image.Image) -> Any:
        """
        Preprocesses a PIL Image for model input.

        Args:
            image (Image.Image): Input PIL Image.

        Returns:
            Any: Hugging Face processor BatchEncoding tensor dict if processor is loaded,
                 otherwise a standard resized RGB PIL Image / PyTorch Tensor dictionary.
        """
        # Ensure image is in RGB mode
        if image.mode != "RGB":
            image = image.convert("RGB")

        # If Hugging Face processor is configured, delegate preprocessing
        if self.hf_processor is not None:
            return self.hf_processor(images=image, return_tensors="pt")

        # Generic preprocessing fallback (resize to target dimensions)
        resized_img = image.resize(self.target_size, Image.Resampling.BILINEAR)
        return resized_img
