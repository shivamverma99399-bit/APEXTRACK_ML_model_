import React from 'react';
import type { TelemetryData, TrendState, TrackCondition } from '../../types/track';

interface MoistureMapPanelProps {
  telemetry: TelemetryData;
  trend?: TrendState;
  condition?: TrackCondition;
}

export const MoistureMapPanel: React.FC<MoistureMapPanelProps> = ({
  telemetry,
  trend = 'insufficient_data',
  condition = 'wet',
}) => {
  const moisturePct =
    condition === 'wet'
      ? 78
      : condition === 'damp'
      ? 44
      : Math.round(telemetry.moistureLevel * 100) || 14;

  const trendLabel =
    trend === 'drying'
      ? 'DRYING'
      : trend === 'wetting'
      ? 'WETTING'
      : trend === 'stable'
      ? 'STABLE'
      : 'MONITORING';

  return (
    <div className="technical-border p-3.5 bg-hud-panel backdrop-blur-md rounded-sm font-mono">
      <div className="flex items-center justify-between mb-2 border-b border-hud-edge/40 pb-1.5">
        <h3 className="data-label text-hud-cyan flex items-center gap-1.5">
          <svg className="w-3 h-3 text-hud-cyan" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
          </svg>
          Moisture Detection
        </h3>
        <span className="text-[7.5px] text-hud-dim">LIVE THERMAL</span>
      </div>

      {/* Top-Down F1 Chassis Moisture Heatmap (from 2.jpg) */}
      <div className="technical-border p-2 bg-hud-bg/70 mb-2 h-28 flex items-center justify-between relative overflow-hidden">
        {/* Car Chassis Vector with Thermal Gradient */}
        <div className="w-20 h-full mx-auto relative flex items-center justify-center">
          <svg className="w-16 h-full" viewBox="0 0 80 120">
            {/* Chassis Outline */}
            <path
              d="M 30 10 Q 40 5 50 10 L 52 30 L 68 35 L 68 45 L 54 48 L 52 75 L 70 85 L 70 98 L 50 96 L 40 115 L 30 96 L 10 98 L 10 85 L 28 75 L 26 48 L 12 45 L 12 35 L 28 30 Z"
              fill="rgba(5, 7, 10, 0.8)"
              stroke="#00f0ff"
              strokeWidth="1.5"
            />
            {/* Thermal Moisture Heat Core */}
            <ellipse
              cx="40"
              cy="65"
              rx="12"
              ry="25"
              fill="url(#moistureGradient)"
              className="animate-pulse"
              opacity="0.85"
            />
            <defs>
              <radialGradient id="moistureGradient" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#00f0ff" stopOpacity="0.9" />
                <stop offset="60%" stopColor="#00ff88" stopOpacity="0.6" />
                <stop offset="100%" stopColor="transparent" stopOpacity="0" />
              </radialGradient>
            </defs>
          </svg>
        </div>

        {/* Vertical Moisture Scale Indicator */}
        <div className="flex flex-col items-center justify-between h-full text-[6.5px] font-bold text-hud-dim pl-1 border-l border-hud-edge/20">
          <span className="text-hud-cyan">WET</span>
          <div className="w-1 flex-1 my-1 bg-hud-edge/30 rounded-full overflow-hidden flex flex-col justify-end">
            <div
              className="w-full bg-gradient-to-t from-hud-green via-hud-amber to-hud-cyan transition-all duration-500 rounded-full"
              style={{ height: `${moisturePct}%` }}
            />
          </div>
          <span className="text-hud-green">DRY</span>
        </div>
      </div>

      {/* Telemetry Metrics (from 2.jpg) */}
      <div className="space-y-1 text-[8.5px]">
        <div className="flex justify-between">
          <span className="text-hud-dim uppercase">Avg Moisture</span>
          <span className="text-white font-bold tabular-nums">{moisturePct}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-hud-dim uppercase">Trend</span>
          <span className="text-hud-cyan font-bold uppercase tracking-wider">{trendLabel}</span>
        </div>
      </div>
    </div>
  );
};
