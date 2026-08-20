import React, { useState, useEffect, useCallback } from 'react';
import { initialApexTrackState } from '../data/initialState';
import type { ApexTrackState, HudNavTab } from '../types/track';
import { checkHealth, analyzeImage, getTrackTrend, ApiError } from '../services/api';
import { TrackVideo } from './hero/TrackVideo';
import { VisionOverlay } from './hero/VisionOverlay';
import { TopHud } from './layout/TopHud';
import { TrackConditionPanel } from './dashboard/TrackConditionPanel';
import { SurfaceAnalysisPanel } from './dashboard/SurfaceAnalysisPanel';
import { MoistureMapPanel } from './dashboard/MoistureMapPanel';
import { ObjectDetectionPanel } from './dashboard/ObjectDetectionPanel';
import { PredictiveAnalysisPanel } from './dashboard/PredictiveAnalysisPanel';
import { TrackTrendPanel } from './strategy/TrackTrendPanel';
import { TireAdvisoryPanel } from './strategy/TireAdvisoryPanel';
import { BottomTelemetry } from './dashboard/BottomTelemetry';
import { SystemAnalysisReadout } from './readout/SystemAnalysisReadout';

export const ApexTrackShell: React.FC = () => {
  const [state, setState] = useState<ApexTrackState>(initialApexTrackState);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>('SYSTEM READY');

  // Sync health and model status with backend
  const syncHealth = useCallback(async () => {
    try {
      const health = await checkHealth();
      setState((prev) => ({
        ...prev,
        systemStatus: health.status === 'healthy' ? 'OPTIMAL' : 'DEGRADED',
        model: {
          ...prev.model,
          configured: health.model?.configured ?? true,
          model_id: health.model?.model_id || prev.model.model_id,
          provider: health.model?.provider || prev.model.provider,
        },
      }));
    } catch {
      setState((prev) => ({
        ...prev,
        systemStatus: 'OFFLINE',
      }));
    }
  }, []);

  // Sync track trend and telemetry history
  const syncTrend = useCallback(async () => {
    try {
      const trendData = await getTrackTrend();
      setState((prev) => ({
        ...prev,
        trend: trendData.trend,
        history: trendData.history,
        advisory: trendData.advisory || prev.advisory,
      }));
    } catch {
      // Keep existing state if trend fetch fails
    }
  }, []);

  // Initial sync on mount
  useEffect(() => {
    syncHealth();
    syncTrend();

    const healthInterval = setInterval(syncHealth, 45000);
    return () => clearInterval(healthInterval);
  }, [syncHealth, syncTrend]);

  // Track active tab dynamically based on scroll position
  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      const heroHeight = window.innerHeight * 0.7;

      if (scrollY < heroHeight) {
        setState((prev) => (prev.activeTab !== 'OVERVIEW' ? { ...prev, activeTab: 'OVERVIEW' } : prev));
        return;
      }

      const sections: { id: string; tab: HudNavTab }[] = [
        { id: 'section-system', tab: 'SYSTEM' },
        { id: 'section-car-status', tab: 'CAR STATUS' },
        { id: 'section-telemetry', tab: 'TELEMETRY' },
        { id: 'section-track-analysis', tab: 'TRACK ANALYSIS' },
      ];

      for (const sec of sections) {
        const el = document.getElementById(sec.id);
        if (el) {
          const rect = el.getBoundingClientRect();
          if (rect.top <= 180) {
            setState((prev) => (prev.activeTab !== sec.tab ? { ...prev, activeTab: sec.tab } : prev));
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Handle image analysis submission
  const handleAnalyzeFile = async (file: File) => {
    setIsAnalyzing(true);
    setErrorMessage(null);
    setStatusMessage('AI INFERENCE PROCESSING...');

    try {
      const response = await analyzeImage(file);

      // Update state with REAL backend response
      setState((prev) => ({
        ...prev,
        condition: response.prediction.condition,
        confidence: response.prediction.confidence,
        probabilities: response.prediction.probabilities,
        processingTimeMs: response.processing_time_ms,
        model: response.model || prev.model,
        trend: response.trend || prev.trend,
        advisory: response.advisory || prev.advisory,
        systemStatus: 'OPTIMAL',
      }));

      setStatusMessage(`AI INFERENCE COMPLETE (${response.processing_time_ms}ms)`);

      // Refresh trend history sequence
      await syncTrend();
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.statusCode === 0) {
          setErrorMessage('MODEL OFFLINE — Unable to reach ApexTrack inference service.');
          setState((prev) => ({ ...prev, systemStatus: 'OFFLINE' }));
        } else if (err.statusCode === 413) {
          setErrorMessage('IMAGE EXCEEDS SIZE LIMIT — Max allowed size is 10MB.');
        } else if (err.statusCode === 415) {
          setErrorMessage('UNSUPPORTED FORMAT — Please upload JPEG, PNG, or WEBP.');
        } else {
          setErrorMessage(err.message || 'Analysis failed.');
        }
      } else {
        setErrorMessage('Unexpected error during track analysis.');
      }
      setStatusMessage(null);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleTabChange = (tab: HudNavTab) => {
    setState((prev) => ({ ...prev, activeTab: tab }));

    if (tab === 'OVERVIEW') {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (tab === 'TRACK ANALYSIS') {
      const el = document.getElementById('section-track-analysis');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
      } else {
        window.scrollTo({ top: window.innerHeight, behavior: 'smooth' });
      }
    } else if (tab === 'CAR STATUS') {
      const el = document.getElementById('section-car-status');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
      } else {
        window.scrollTo({ top: window.innerHeight * 2, behavior: 'smooth' });
      }
    } else if (tab === 'TELEMETRY') {
      const el = document.getElementById('section-telemetry');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
      } else {
        window.scrollTo({ top: window.innerHeight * 1.5, behavior: 'smooth' });
      }
    } else if (tab === 'SYSTEM') {
      const el = document.getElementById('section-system');
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
      } else {
        window.scrollTo({ top: window.innerHeight * 2.5, behavior: 'smooth' });
      }
    }
  };

  const scrollToReadout = () => {
    const el = document.getElementById('section-track-analysis');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    } else {
      window.scrollTo({
        top: window.innerHeight - 30,
        behavior: 'smooth',
      });
    }
  };

  return (
    <div className="relative w-full min-h-screen bg-black text-hud-txt font-mono scanlines select-none overflow-x-hidden">
      {/* ========================================================
          PERSISTENT TOP TECHNICAL HUD
         ======================================================== */}
      <TopHud
        model={state.model}
        condition={state.condition}
        cameraName={state.cameraName}
        frameCount={state.frameCount}
        systemStatus={state.systemStatus}
        activeTab={state.activeTab}
        onTabChange={handleTabChange}
        airTemp={state.telemetry.airTemp}
      />

      {/* ========================================================
          SECTION 0: APEXTRACK LIVE COMMAND CENTER (HERO 100VH)
         ======================================================== */}
      <section id="section-overview" className="relative w-full h-screen min-h-screen overflow-hidden">
        {/* 1. Central Hero Video */}
        <TrackVideo
          videoSrc="/assets/videos/apextrack-track.mp4"
          cameraName={state.cameraName}
          circuitName={state.circuitName}
        />

        {/* 2. Computer Vision Overlays */}
        <VisionOverlay
          condition={state.condition}
          gripLevel={state.telemetry.gripLevel}
          turnData={state.telemetry.turnData}
        />

        {/* 3. Floating HUD Panels */}
        <main className="relative z-30 w-full h-full pt-14 pb-[160px] px-3.5 flex justify-between pointer-events-none">
          {/* Left Column */}
          <aside className="w-72 lg:w-80 h-full flex flex-col gap-2.5 overflow-y-auto pointer-events-auto pr-1">
            <TrackConditionPanel
              condition={state.condition}
              confidence={state.confidence}
              probabilities={state.probabilities}
              processingTimeMs={state.processingTimeMs}
              isAnalyzing={isAnalyzing}
              onAnalyzeFile={handleAnalyzeFile}
              errorMessage={errorMessage}
              statusMessage={statusMessage}
            />

            <SurfaceAnalysisPanel telemetry={state.telemetry} />

            <MoistureMapPanel
              telemetry={state.telemetry}
              trend={state.trend}
              condition={state.condition}
            />
          </aside>

          {/* Right Column */}
          <aside className="w-72 lg:w-80 h-full flex flex-col gap-2.5 overflow-y-auto pointer-events-auto pl-1">
            <ObjectDetectionPanel objects={state.telemetry.objectDetection} />

            <PredictiveAnalysisPanel
              lapTime={state.telemetry.lapTime}
              delta={state.telemetry.delta}
              tyreDegradation={state.telemetry.tyreDegradation}
              fuelLoad={state.telemetry.fuelLoad}
            />

            <TrackTrendPanel
              trend={state.trend}
              history={state.history}
            />

            <TireAdvisoryPanel advisory={state.advisory} />
          </aside>
        </main>

        {/* 4. Bottom Telemetry */}
        <BottomTelemetry telemetry={state.telemetry} />

        {/* 5. Subtle Scroll Down Indicator */}
        <button
          type="button"
          onClick={scrollToReadout}
          className="absolute bottom-2 left-1/2 transform -translate-x-1/2 z-40 flex flex-col items-center gap-1 text-[8.5px] text-hud-cyan tracking-[0.2em] font-bold uppercase transition-all duration-300 hover:scale-105 cursor-pointer bg-hud-bg/80 px-3 py-1 rounded-full border border-hud-cyan/40 shadow-[0_0_12px_rgba(0,240,255,0.3)] pointer-events-auto"
        >
          <span className="flex items-center gap-1.5">
            <span>SCROLL TO ANALYZE</span>
            <span className="animate-bounce">↓</span>
          </span>
          <span className="text-[6.5px] text-hud-dim tracking-widest">
            VIEW ENGINEERING DATA
          </span>
        </button>
      </section>

      {/* ========================================================
          SECTIONS 01 - 10: DETAILED SYSTEM READOUT (SCROLL-DOWN)
         ======================================================== */}
      <SystemAnalysisReadout state={state} />
    </div>
  );
};
