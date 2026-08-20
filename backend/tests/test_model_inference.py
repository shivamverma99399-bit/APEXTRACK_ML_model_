from PIL import Image
from app.ml.predictor import HFTrackConditionPredictor
from app.schemas.prediction import TrackConditionEnum


def test_real_model_inference():
    """
    Test real ViT model inference, dynamic id2label mapping, and probability sum constraints.
    """
    predictor = HFTrackConditionPredictor()
    # Create test RGB image
    test_img = Image.new("RGB", (224, 224), color=(128, 128, 128))

    result = predictor.predict(test_img)

    assert result.condition in [TrackConditionEnum.DRY, TrackConditionEnum.DAMP, TrackConditionEnum.WET]
    assert 0.0 <= result.confidence <= 1.0
    assert set(result.probabilities.keys()) == {"dry", "damp", "wet"}

    prob_sum = sum(result.probabilities.values())
    assert 0.98 <= prob_sum <= 1.02
