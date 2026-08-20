import React from 'react';
import type { ObjectDetectionData } from '../../types/track';

interface ObjectDetectionPanelProps {
  objects?: ObjectDetectionData;
}

export const ObjectDetectionPanel: React.FC<ObjectDetectionPanelProps> = ({
  objects = { car: 1, marshal: 0, debris: 0, flag: 0 },
}) => {
  return (
    <div className="technical-border p-3.5 bg-hud-panel backdrop-blur-md rounded-sm font-mono">
      <div className="flex items-center justify-between mb-2.5 border-b border-hud-edge/40 pb-1.5">
        <h3 className="data-label text-hud-cyan flex items-center gap-1.5">
          <svg className="w-3 h-3 text-hud-cyan" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2" />
          </svg>
          Object Detection
        </h3>
        <span className="text-[7.5px] text-hud-dim">LIVE RADAR</span>
      </div>

      <div className="space-y-1.5 text-[8.5px]">
        {/* Race Car */}
        <div className="flex justify-between items-center px-2 py-1 bg-hud-cyan/10 border-l-2 border-hud-cyan rounded-xs">
          <span className="text-white font-bold flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-hud-cyan" />
            RACE CAR
          </span>
          <span className="text-hud-cyan font-bold tabular-nums">{objects.car} <span className="text-[7px] text-hud-dim">TRACK</span></span>
        </div>

        {/* Marshal */}
        <div className="flex justify-between items-center px-2 py-1 border-l-2 border-transparent">
          <span className="text-hud-dim uppercase">Marshal</span>
          <span className="text-hud-dim tabular-nums">{objects.marshal} <span className="text-[7px]">TRACK</span></span>
        </div>

        {/* Debris */}
        <div className="flex justify-between items-center px-2 py-1 border-l-2 border-transparent">
          <span className="text-hud-dim uppercase">Debris</span>
          <span className="text-hud-dim tabular-nums">{objects.debris} <span className="text-[7px]">TRACK</span></span>
        </div>

        {/* Track Limit / Flag */}
        <div className="flex justify-between items-center px-2 py-1 border-l-2 border-transparent">
          <span className="text-hud-dim uppercase">Track Limit</span>
          <span className="text-hud-dim tabular-nums">{objects.flag} <span className="text-[7px]">TRACK</span></span>
        </div>
      </div>
    </div>
  );
};
