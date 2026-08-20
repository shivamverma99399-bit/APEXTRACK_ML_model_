import React from 'react';
import type { TyreDegradation } from '../../types/track';

interface PredictiveAnalysisPanelProps {
  lapTime?: string;
  delta?: string;
  tyreDegradation?: TyreDegradation;
  fuelLoad?: string;
}

export const PredictiveAnalysisPanel: React.FC<PredictiveAnalysisPanelProps> = ({
  lapTime = '01:24.652',
  delta = '-0.236',
  tyreDegradation = { fl: 12, fr: 13, rl: 11, rr: 11 },
  fuelLoad = '36.7 LAPS',
}) => {
  return (
    <div className="technical-border p-3.5 bg-hud-panel backdrop-blur-md rounded-sm font-mono">
      <div className="flex items-center justify-between mb-2.5 border-b border-hud-edge/40 pb-1.5">
        <h3 className="data-label text-hud-cyan flex items-center gap-1.5">
          <svg className="w-3 h-3 text-hud-cyan" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
          </svg>
          Predictive Analysis
        </h3>
        <span className="text-[7.5px] text-hud-green font-bold">DELTA ACTIVE</span>
      </div>

      {/* Lap Time & Delta */}
      <div className="space-y-1 text-[8.5px] mb-2.5 pb-2 border-b border-hud-edge/30">
        <div className="flex justify-between">
          <span className="text-hud-dim uppercase">Lap Time</span>
          <span className="text-white font-bold tabular-nums">{lapTime}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-hud-dim uppercase">Delta</span>
          <span className="text-hud-green font-bold tabular-nums">{delta} s</span>
        </div>
      </div>

      {/* Tyre Degradation */}
      <div className="mb-2.5">
        <p className="data-label !text-[7px] text-hud-dim mb-1.5 uppercase">Tyre Degradation</p>
        <div className="grid grid-cols-2 gap-x-3 gap-y-1 text-[8px]">
          <div className="flex justify-between">
            <span className="text-hud-dim">FRONT LEFT</span>
            <span className="text-white font-bold">{tyreDegradation.fl}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-hud-dim">FRONT RIGHT</span>
            <span className="text-white font-bold">{tyreDegradation.fr}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-hud-dim">REAR LEFT</span>
            <span className="text-white font-bold">{tyreDegradation.rl}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-hud-dim">REAR RIGHT</span>
            <span className="text-white font-bold">{tyreDegradation.rr}%</span>
          </div>
        </div>
      </div>

      {/* Fuel Load */}
      <div className="flex justify-between items-center text-[8.5px] pt-1.5 border-t border-hud-edge/30">
        <span className="text-hud-dim uppercase font-bold">Fuel Load</span>
        <span className="text-hud-cyan font-bold tabular-nums">{fuelLoad}</span>
      </div>
    </div>
  );
};
