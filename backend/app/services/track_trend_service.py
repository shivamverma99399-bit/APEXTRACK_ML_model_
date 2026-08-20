from collections import deque
from datetime import datetime, timezone
from typing import List, Optional
from app.core.config import settings
from app.schemas.prediction import TrackConditionEnum
from app.schemas.trend import HistoryItem, TrackTrendResponse, TrendEnum
from app.services.tire_advisory_service import TireAdvisoryService


CONDITION_LEVELS = {
    TrackConditionEnum.DRY: 0,
    TrackConditionEnum.DAMP: 1,
    TrackConditionEnum.WET: 2,
}


class TrackTrendService:
    """
    Temporal Track Condition Trend Engine.
    Tracks chronological sequences of predictions in bounded memory,
    filters for reliable confidence, and calculates dynamic track transitions (drying, wetting, stable).
    """

    def __init__(self, max_history: Optional[int] = None, min_confidence: Optional[float] = None):
        self.max_history = max_history or settings.MAX_HISTORY
        self.min_confidence = min_confidence if min_confidence is not None else settings.TREND_MIN_CONFIDENCE
        self._history: deque = deque(maxlen=self.max_history)

    def add_prediction(
        self,
        condition: TrackConditionEnum,
        confidence: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Records a new prediction in the chronological history buffer.
        """
        ts = timestamp or datetime.now(timezone.utc)
        item = HistoryItem(
            timestamp=ts,
            condition=condition,
            confidence=confidence,
        )
        self._history.append(item)

    def get_history(self) -> List[HistoryItem]:
        """
        Returns a list of recorded prediction history items in chronological order.
        """
        return list(self._history)

    def clear_history(self) -> None:
        """
        Clears the in-memory history buffer.
        """
        self._history.clear()

    def calculate_trend(self) -> TrendEnum:
        """
        Calculates the temporal trend from recent reliable predictions.
        Rules:
        - Filters history for predictions with confidence >= min_confidence.
        - Requires at least 3 reliable predictions, otherwise returns INSUFFICIENT_DATA.
        - Analyzes directional trend across ordered levels (dry=0, damp=1, wet=2).
        """
        reliable_items = [
            item for item in self._history
            if item.confidence >= self.min_confidence
        ]

        if len(reliable_items) < 3:
            return TrendEnum.INSUFFICIENT_DATA

        # Use the most recent window of reliable observations (up to 10)
        window = reliable_items[-10:]
        levels = [CONDITION_LEVELS[item.condition] for item in window]

        first_half = levels[: len(levels) // 2]
        second_half = levels[len(levels) // 2 :]

        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        delta = avg_second - avg_first

        # Overall start-to-end delta
        total_delta = levels[-1] - levels[0]

        if total_delta < 0 or delta < -0.3:
            return TrendEnum.DRYING
        elif total_delta > 0 or delta > 0.3:
            return TrendEnum.WETTING
        else:
            return TrendEnum.STABLE

    def get_trend_response(self) -> TrackTrendResponse:
        """
        Constructs the comprehensive trend and advisory response.
        """
        history_list = self.get_history()
        trend = self.calculate_trend()
        latest_condition = history_list[-1].condition if history_list else None
        latest_confidence = history_list[-1].confidence if history_list else 0.0

        advisory = TireAdvisoryService.generate_advisory(
            current_condition=latest_condition,
            trend=trend,
            confidence=latest_confidence,
        )

        return TrackTrendResponse(
            history=history_list,
            trend=trend,
            advisory=advisory,
        )


# Global singleton instance for in-memory session persistence
track_trend_service_instance = TrackTrendService()
