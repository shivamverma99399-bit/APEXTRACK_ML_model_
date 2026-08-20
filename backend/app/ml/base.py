from abc import ABC, abstractmethod
from PIL import Image
from app.schemas.analysis import ModelMetadata
from app.schemas.prediction import PredictionResult


class TrackConditionPredictor(ABC):
    """
    Abstract base interface for track condition predictors.
    All ML model implementations (Hugging Face vision models, local fine-tuned models, etc.)
    must implement this interface.
    """

    @abstractmethod
    def predict(self, image: Image.Image) -> PredictionResult:
        """
        Processes a preprocessed RGB PIL image and returns standard PredictionResult.

        Args:
            image (Image.Image): RGB PIL Image object.

        Returns:
            PredictionResult: Strongly typed prediction result containing condition, confidence, and probabilities.
        """
        pass

    @abstractmethod
    def get_model_info(self) -> ModelMetadata:
        """
        Returns metadata about the active ML model.

        Returns:
            ModelMetadata: Provider and model identifier info.
        """
        pass
