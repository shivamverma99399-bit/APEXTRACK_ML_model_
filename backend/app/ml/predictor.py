from typing import Optional
from PIL import Image
import torch
import torch.nn.functional as F

from app.core.exceptions import (
    InferenceException,
    ModelNotConfiguredException,
)
from app.core.logging import logger
from app.ml.base import TrackConditionPredictor
from app.ml.model_loader import HFModelLoader
from app.ml.preprocessing import ImagePreprocessor
from app.schemas.analysis import ModelMetadata
from app.schemas.prediction import PredictionResult, TrackConditionEnum


class HFTrackConditionPredictor(TrackConditionPredictor):
    """
    Hugging Face Vision Predictor for live racing track condition classification.
    Uses cached model instance, runs with torch.no_grad(), and extracts softmax probabilities.
    """

    def __init__(self, model_id_or_path: Optional[str] = None):
        self.model_id = model_id_or_path or HFModelLoader.get_configured_model_target() or ""
        self.model = None
        self.processor = None
        self.preprocessor = None

        if HFModelLoader.is_configured():
            try:
                self.model, self.processor = HFModelLoader.load_model_and_processor(
                    model_id_or_path=self.model_id
                )
                self.preprocessor = ImagePreprocessor(hf_processor=self.processor)
            except Exception as e:
                logger.warning(f"Could not initialize Hugging Face predictor: {str(e)}")

    def predict(self, image: Image.Image) -> PredictionResult:
        """
        Performs inference using the loaded model.
        """
        if self.model is None or self.preprocessor is None:
            # Attempt lazy load
            try:
                self.model, self.processor = HFModelLoader.load_model_and_processor(
                    model_id_or_path=self.model_id
                )
                self.preprocessor = ImagePreprocessor(hf_processor=self.processor)
            except Exception as e:
                raise ModelNotConfiguredException(
                    f"Hugging Face vision model is not loaded: {str(e)}"
                )

        try:
            device = next(self.model.parameters()).device
            inputs = self.preprocessor.preprocess(image)
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.inference_mode():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = F.softmax(logits, dim=-1).squeeze().tolist()

            del inputs, outputs, logits

            if isinstance(probs, float):
                probs = [probs]

            # Dynamic id2label mapping from model config
            id2label = getattr(self.model.config, "id2label", {0: "damp", 1: "dry", 2: "wet"})

            probabilities_dict = {"dry": 0.0, "damp": 0.0, "wet": 0.0}

            for idx, prob_val in enumerate(probs):
                label_name = str(id2label.get(idx, str(idx))).lower().strip()
                if label_name in probabilities_dict:
                    probabilities_dict[label_name] = round(float(prob_val), 4)

            # Determine primary predicted condition
            best_condition = max(probabilities_dict, key=probabilities_dict.get)
            confidence = probabilities_dict[best_condition]

            return PredictionResult(
                condition=TrackConditionEnum(best_condition),
                confidence=confidence,
                probabilities=probabilities_dict,
            )
        except Exception as e:
            logger.error(f"Inference error in HFTrackConditionPredictor: {str(e)}", exc_info=True)
            raise InferenceException(f"Failed to execute vision model inference: {str(e)}")

    def get_model_info(self) -> ModelMetadata:
        target = self.model_id or HFModelLoader.get_configured_model_target() or "unconfigured"
        return ModelMetadata(
            provider="huggingface",
            model_id=target,
        )


class MockPredictor(TrackConditionPredictor):
    """
    Mock Predictor for unit testing and local developer API contract testing ONLY.
    """

    def __init__(
        self,
        condition: TrackConditionEnum = TrackConditionEnum.WET,
        confidence: float = 0.91,
        probabilities: Optional[dict] = None,
    ):
        self.condition = condition
        self.confidence = confidence
        self.probabilities = probabilities or {
            "dry": 0.03,
            "damp": 0.06,
            "wet": 0.91,
        }

    def predict(self, image: Image.Image) -> PredictionResult:
        return PredictionResult(
            condition=self.condition,
            confidence=self.confidence,
            probabilities=self.probabilities,
        )

    def get_model_info(self) -> ModelMetadata:
        return ModelMetadata(
            provider="mock-test-stub",
            model_id="apextrack/mock-predictor-stub",
        )
