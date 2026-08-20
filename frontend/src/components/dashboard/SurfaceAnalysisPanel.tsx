import React from 'react';
import type { TelemetryData } from '../../types/track';

interface SurfaceAnalysisPanelProps {
  telemetry: TelemetryData;
}

export const SurfaceAnalysisPanel: React.FC<SurfaceAnalysisPanelProps> = ({ telemetry }) => {
  const { trackFeatures } = telemetry;

  return (
    <div className="technical-border p-3.5 bg-hud-panel backdrop-blur-md rounded-sm font-mono">
      {/* 1. Track Analysis Section (from 2.jpg) */}
      <div className="mb-3 pb-2.5 border-b border-hud-edge/40">
        <h3 className="data-label text-hud-cyan mb-2 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-hud-cyan animate-pulse" />
            Track Analysis
          </span>
          <span className="text-[7px] text-hud-dim">SPA RADAR</span>
        </h3>

        <div className="space-y-1.5 text-[8.5px]">
          {/* Racing Line */}
          <div className="flex justify-between items-center">
            <span className="text-hud-dim flex items-center gap-1">
              <span className="text-hud-cyan text-[9px]">◇</span> RACING LINE
            </span>
            <span className="text-white font-bold">
              {trackFeatures?.racingLine?.status || 'OPTIMAL'} <span className="text-[7.5px] text-hud-dim">{trackFeatures?.racingLine?.confidence || 98}%</span>
            </span>
          </div>

          {/* Braking Zone */}
          <div className="flex justify-between items-center">
            <span className="text-hud-dim flex items-center gap-1">
              <span className="text-hud-amber text-[9px]">△</span> BRAKING ZONE
            </span>
            <span className="text-white font-bold">
              {trackFeatures?.brakingZone?.distance || 'AHEAD 120m'} <span className="text-[7.5px] text-hud-dim">{trackFeatures?.brakingZone?.confidence || 95}%</span>
            </span>
          </div>

          {/* Turn Apex */}
          <div className="flex justify-between items-center">
            <span className="text-hud-dim flex items-center gap-1">
              <span className="text-hud-green text-[9px]">✦</span> TURN APEX
            </span>
            <span className="text-white font-bold">
              CONFIDENCE {trackFeatures?.turnApex?.confidence || 97}%
            </span>
          </div>

          {/* DRS Zone */}
          <div className="flex justify-between items-center">
            <span className="text-hud-dim flex items-center gap-1">
              <span className="text-hud-cyan text-[9px]">◎</span> DRS ZONE
            </span>
            <span className="text-white font-bold">
              {trackFeatures?.drsZone?.distance || 'DETECTION 240m'} <span className="text-[7.5px] text-hud-dim">{trackFeatures?.drsZone?.confidence || 99}%</span>
            </span>
          </div>
        </div>
      </div>

      {/* 2. Surface Analysis Section (from 2.jpg) */}
      <div>
        <h3 className="data-label text-hud-cyan mb-2">Surface Analysis</h3>
        <div className="space-y-1 text-[8.5px]">
          <div className="flex justify-between">
            <span className="text-hud-dim uppercase">Grip Level</span>
            <span className="text-white font-bold">{telemetry.gripStatus || 'MEDIUM'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-hud-dim uppercase">Surface Temp</span>
            <span className="text-white font-bold">{telemetry.trackTemp} °C</span>
          </div>
          <div className="flex justify-between">
            <span className="text-hud-dim uppercase">Irregularities</span>
            <span className="text-white font-bold">{telemetry.irregularities || 2.1}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-hud-dim uppercase">Wear Level</span>
            <span className="text-hud-cyan font-bold">MEDIUM</span>
          </div>
        </div>
      </div>
    </div>
  );
};
