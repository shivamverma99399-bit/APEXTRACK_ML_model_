import time
from datetime import datetime, timezone
from typing import Optional
import uuid
from fastapi import UploadFile
from app.core.logging import logger
from app.ml.base import TrackConditionPredictor
from app.schemas.analysis import ImageAnalysisResponse
from app.services.image_service import ImageService
from app.services.track_trend_service import TrackTrendService, track_trend_service_instance
from app.services.tire_advisory_service import TireAdvisoryService


class AnalysisService:
    """
    Service coordinating track condition analysis workflow.
    Executes vision inference and updates temporal track trends and tire advisories.
    """

    def __init__(
        self,
        image_service: ImageService,
        predictor: TrackConditionPredictor,
        trend_service: Optional[TrackTrendService] = None,
    ):
        self.image_service = image_service
        self.predictor = predictor
        self.trend_service = trend_service or track_trend_service_instance

    async def analyze_image(self, file: UploadFile) -> ImageAnalysisResponse:
        """
        Executes track image analysis pipeline:
        1. Read and validate uploaded image file bytes.
        2. Execute prediction using injected TrackConditionPredictor.
        3. Record observation in temporal trend engine.
        4. Measure processing duration.
        5. Construct and return normalized ImageAnalysisResponse.
        """
        start_time = time.perf_counter()
        analysis_id = uuid.uuid4()
        timestamp = datetime.now(timezone.utc)

        logger.info(f"Starting track condition analysis session [{analysis_id}]")

        # Step 1: Validate and decode uploaded image
        pil_image, _ = await self.image_service.process_upload(file)

        # Step 2: Perform ML inference using predictor interface
        prediction = self.predictor.predict(pil_image)

        # Step 3: Record in temporal trend service
        self.trend_service.add_prediction(
            condition=prediction.condition,
            confidence=prediction.confidence,
            timestamp=timestamp,
        )

        trend = self.trend_service.calculate_trend()
        advisory = TireAdvisoryService.generate_advisory(
            current_condition=prediction.condition,
            trend=trend,
            confidence=prediction.confidence,
        )

        # Step 4: Measure execution time in milliseconds
        end_time = time.perf_counter()
        processing_time_ms = round((end_time - start_time) * 1000, 2)

        model_info = self.predictor.get_model_info()

        logger.info(
            f"Analysis session [{analysis_id}] completed in {processing_time_ms} ms. "
            f"Result: condition='{prediction.condition.value}', confidence={prediction.confidence:.2f}, trend='{trend.value}'"
        )

        # Step 5: Return normalized API response schema
        return ImageAnalysisResponse(
            analysis_id=analysis_id,
            timestamp=timestamp,
            prediction=prediction,
            processing_time_ms=processing_time_ms,
            model=model_info,
            trend=trend,
            advisory=advisory,
        )
