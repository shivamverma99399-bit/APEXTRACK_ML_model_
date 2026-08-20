from app.schemas.prediction import TrackConditionEnum
from app.schemas.trend import TrendEnum
from app.services.tire_advisory_service import TireAdvisoryService
from app.services.track_trend_service import TrackTrendService


def test_trend_insufficient_data():
    service = TrackTrendService(min_confidence=0.55)
    # 0 predictions
    assert service.calculate_trend() == TrendEnum.INSUFFICIENT_DATA

    # 2 reliable predictions
    service.add_prediction(TrackConditionEnum.WET, 0.8)
    service.add_prediction(TrackConditionEnum.DAMP, 0.8)
    assert service.calculate_trend() == TrendEnum.INSUFFICIENT_DATA


def test_trend_low_confidence_filtering():
    service = TrackTrendService(min_confidence=0.6)
    service.add_prediction(TrackConditionEnum.WET, 0.8)
    service.add_prediction(TrackConditionEnum.DAMP, 0.4)  # ignored due to low confidence
    service.add_prediction(TrackConditionEnum.DRY, 0.8)
    # Only 2 reliable predictions exist
    assert service.calculate_trend() == TrendEnum.INSUFFICIENT_DATA


def test_trend_drying_sequence():
    service = TrackTrendService(min_confidence=0.5)
    service.add_prediction(TrackConditionEnum.WET, 0.85)
    service.add_prediction(TrackConditionEnum.DAMP, 0.80)
    service.add_prediction(TrackConditionEnum.DRY, 0.90)

    assert service.calculate_trend() == TrendEnum.DRYING


def test_trend_wetting_sequence():
    service = TrackTrendService(min_confidence=0.5)
    service.add_prediction(TrackConditionEnum.DRY, 0.85)
    service.add_prediction(TrackConditionEnum.DAMP, 0.80)
    service.add_prediction(TrackConditionEnum.WET, 0.90)

    assert service.calculate_trend() == TrendEnum.WETTING


def test_trend_stable_sequence():
    service = TrackTrendService(min_confidence=0.5)
    service.add_prediction(TrackConditionEnum.WET, 0.85)
    service.add_prediction(TrackConditionEnum.WET, 0.88)
    service.add_prediction(TrackConditionEnum.WET, 0.82)

    assert service.calculate_trend() == TrendEnum.STABLE


def test_tire_advisory_rules():
    # Wet + Drying
    adv = TireAdvisoryService.generate_advisory(TrackConditionEnum.WET, TrendEnum.DRYING, 0.8)
    assert adv.severity == "medium"
    assert "drying" in adv.message.lower()

    # Dry + Wetting
    adv = TireAdvisoryService.generate_advisory(TrackConditionEnum.DRY, TrendEnum.WETTING, 0.9)
    assert adv.severity == "high"
    assert "deteriorating" in adv.message.lower()

    # Dry + Stable
    adv = TireAdvisoryService.generate_advisory(TrackConditionEnum.DRY, TrendEnum.STABLE, 0.9)
    assert adv.severity == "low"
    assert "dry" in adv.message.lower()
