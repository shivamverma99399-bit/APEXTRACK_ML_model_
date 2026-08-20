import React from 'react';
import type { TelemetryData } from '../../types/track';

interface TireStatusPanelProps {
  telemetry: TelemetryData;
}

export const TireStatusPanel: React.FC<TireStatusPanelProps> = ({ telemetry }) => {
  const { fl, fr, rl, rr } = telemetry.tyreTelemetry;

  return (
    <div className="technical-border p-4 bg-hud-panel backdrop-blur-md rounded-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="data-label text-hud-cyan uppercase">Tyre Temperature & Pressure</h3>
        <span className="text-[8px] text-hud-dim">P-ZERO INTER</span>
      </div>

      <div className="flex items-center gap-4">
        {/* Car Skeleton Blueprint */}
        <div className="w-14 h-24 border border-hud-edge/30 relative rounded-sm flex flex-col justify-between p-1 bg-hud-bg/50">
          <div className="flex justify-between">
            <div className="w-3.5 h-5 bg-hud-cyan/25 border border-hud-cyan/50 rounded-xs" />
            <div className="w-3.5 h-5 bg-hud-cyan/25 border border-hud-cyan/50 rounded-xs" />
          </div>
          {/* Chassis Line */}
          <div className="w-[1px] h-8 bg-hud-edge/40 mx-auto" />
          <div className="flex justify-between">
            <div className="w-3.5 h-5 bg-hud-cyan/25 border border-hud-cyan/50 rounded-xs" />
            <div className="w-3.5 h-5 bg-hud-cyan/25 border border-hud-cyan/50 rounded-xs" />
          </div>
        </div>

        {/* 4 Corners Telemetry Data */}
        <div className="flex-1 grid grid-cols-1 gap-1.5 font-mono">
          <div className="flex justify-between items-center text-[8.5px] border-b border-hud-edge/20 pb-0.5">
            <span className="text-hud-cyan font-bold">FL</span>
            <span className="text-white">{fl.pressure} bar | {fl.temp}°C</span>
          </div>
          <div className="flex justify-between items-center text-[8.5px] border-b border-hud-edge/20 pb-0.5">
            <span className="text-hud-cyan font-bold">FR</span>
            <span className="text-white">{fr.pressure} bar | {fr.temp}°C</span>
          </div>
          <div className="flex justify-between items-center text-[8.5px] border-b border-hud-edge/20 pb-0.5">
            <span className="text-hud-cyan font-bold">RL</span>
            <span className="text-white">{rl.pressure} bar | {rl.temp}°C</span>
          </div>
          <div className="flex justify-between items-center text-[8.5px]">
            <span className="text-hud-cyan font-bold">RR</span>
            <span className="text-white">{rr.pressure} bar | {rr.temp}°C</span>
          </div>
        </div>
      </div>
    </div>
  );
};
