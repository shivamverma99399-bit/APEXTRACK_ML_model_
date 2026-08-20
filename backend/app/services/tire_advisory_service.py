from typing import Optional
from app.schemas.prediction import TrackConditionEnum
from app.schemas.trend import TireAdvisory, TrendEnum


class TireAdvisoryService:
    """
    Decision-support tire advisory engine.
    Analyzes instantaneous track condition, temporal trend, and prediction confidence
    to generate tactical engineering advisories.
    """

    @staticmethod
    def generate_advisory(
        current_condition: Optional[TrackConditionEnum],
        trend: TrendEnum,
        confidence: float = 0.0,
    ) -> TireAdvisory:
        """
        Generates tactical tire advisory based on condition and trend.
        Uses cautious decision-support language ('Consider', 'Monitor', 'May be approaching').
        """
        if trend == TrendEnum.INSUFFICIENT_DATA or current_condition is None:
            return TireAdvisory(
                severity="low",
                message="Telemetry sequence initializing. Continue monitoring live track feed.",
                recommended_action="Maintain current tire setup and observe track conditions.",
            )

        cond = current_condition.value.lower() if isinstance(current_condition, TrackConditionEnum) else str(current_condition).lower()

        if cond == "wet":
            if trend == TrendEnum.DRYING:
                return TireAdvisory(
                    severity="medium",
                    message="Track is drying. Tire-change window may be approaching.",
                    recommended_action="Prepare intermediate or slick tire change window.",
                )
            elif trend == TrendEnum.WETTING:
                return TireAdvisory(
                    severity="high",
                    message="Track surface moisture intensifying.",
                    recommended_action="Maintain full wet tire compound; monitor for standing water.",
                )
            else:  # STABLE
                return TireAdvisory(
                    severity="high",
                    message="Track remains wet. Continue monitoring conditions.",
                    recommended_action="Maintain wet-weather tire compound strategy.",
                )

        elif cond == "damp":
            if trend == TrendEnum.DRYING:
                return TireAdvisory(
                    severity="medium",
                    message="Track is approaching dry conditions. Monitor tire-change timing.",
                    recommended_action="Consider transition to dry compound as dry line emerges.",
                )
            elif trend == TrendEnum.WETTING:
                return TireAdvisory(
                    severity="high",
                    message="Track moisture increasing. Conditions deteriorating toward wet.",
                    recommended_action="Prepare for wet-weather tire switch.",
                )
            else:  # STABLE
                return TireAdvisory(
                    severity="medium",
                    message="Track moisture stable in damp range. Variable grip levels.",
                    recommended_action="Monitor tire temperature and track drying progression.",
                )

        elif cond == "dry":
            if trend == TrendEnum.WETTING:
                return TireAdvisory(
                    severity="high",
                    message="Track conditions are deteriorating. Moisture accumulation detected.",
                    recommended_action="Monitor radar and prepare wet/intermediate tire strategy.",
                )
            elif trend == TrendEnum.DRYING:
                return TireAdvisory(
                    severity="low",
                    message="Track surface fully dry with stabilized grip levels.",
                    recommended_action="Maintain standard slick tire compound strategy.",
                )
            else:  # STABLE
                return TireAdvisory(
                    severity="low",
                    message="Track appears dry. Dry-weather conditions detected.",
                    recommended_action="Maintain optimal dry slick tire strategy.",
                )

        # Fallback default
        return TireAdvisory(
            severity="low",
            message="Track condition monitored. Strategy nominal.",
            recommended_action="Continue standard race strategy monitoring.",
        )
