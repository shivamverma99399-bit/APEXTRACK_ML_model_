import React from 'react';
import type { TrackCondition, TurnData } from '../../types/track';

interface VisionOverlayProps {
  condition: TrackCondition;
  gripLevel?: number;
  turnData?: TurnData;
}

export const VisionOverlay: React.FC<VisionOverlayProps> = ({
  condition,
  gripLevel = 0.42,
  turnData = { turnNumber: 12, apexSpeed: 245, entrySpeed: 198, gear: 6 },
}) => {
  const isWet = condition === 'wet';
  const isDamp = condition === 'damp';

  return (
    <div className="absolute inset-0 w-full h-full pointer-events-none z-10 overflow-hidden font-mono select-none">
      {/* 1. Turn 12 Tactical Radar Card (Top Left of Center, from 2.jpg) */}
      <div className="absolute top-16 left-76 lg:left-88 technical-border bg-hud-panel/80 backdrop-blur-md p-3 rounded-sm border border-hud-edge/40 shadow-[0_0_20px_rgba(0,0,0,0.7)] flex gap-4 items-center">
        <div>
          <div className="flex items-center gap-1.5 mb-1">
            <span className="w-1.5 h-1.5 rounded-full bg-hud-cyan animate-pulse" />
            <h4 className="text-[10px] text-white font-extrabold tracking-wider uppercase">
              TURN {turnData.turnNumber}
            </h4>
          </div>
          <div className="space-y-0.5 text-[8.5px]">
            <div className="flex justify-between gap-3 text-hud-dim">
              <span>APEX SPEED</span>
              <span className="text-white font-bold">{turnData.apexSpeed} <span className="text-[7px]">KM/H</span></span>
            </div>
            <div className="flex justify-between gap-3 text-hud-dim">
              <span>ENTRY SPEED</span>
              <span className="text-white font-bold">{turnData.entrySpeed} <span className="text-[7px]">KM/H</span></span>
            </div>
            <div className="flex justify-between gap-3 text-hud-dim">
              <span>GEAR</span>
              <span className="text-hud-cyan font-bold">{turnData.gear}</span>
            </div>
          </div>
        </div>

        {/* Mini Turn Silhouette */}
        <div className="w-12 h-12 border-l border-hud-edge/30 pl-3 flex items-center justify-center relative">
          <svg className="w-9 h-9 opacity-80" viewBox="0 0 100 100">
            <path d="M20 80 Q 50 10 80 50 T 90 90" fill="none" stroke="#8a95a8" strokeWidth="3" />
            <circle cx="50" cy="30" r="4" fill="#00f0ff" className="animate-ping" />
            <circle cx="50" cy="30" r="3" fill="#00f0ff" />
          </svg>
        </div>
      </div>

      {/* 2. Tactical Surface Mesh Grid Scanners on Track (from 2.jpg) */}
      {/* Yellow Grid Patch on Left */}
      <div
        className="absolute border border-hud-amber/50 bg-hud-amber/5 opacity-60 transform -skew-x-12"
        style={{
          top: '38%',
          left: '18%',
          width: '140px',
          height: '110px',
          backgroundImage:
            'linear-gradient(rgba(255,176,0,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255,176,0,0.3) 1px, transparent 1px)',
          backgroundSize: '14px 14px',
        }}
      >
        <span className="absolute -top-3.5 left-1 text-[7px] text-hud-amber font-mono font-bold">
          KERB SCAN [OPTIMAL]
        </span>
      </div>

      {/* Cyan Grid Patch on Right */}
      <div
        className="absolute border border-hud-cyan/50 bg-hud-cyan/5 opacity-60 transform skew-x-12"
        style={{
          top: '38%',
          right: '20%',
          width: '150px',
          height: '100px',
          backgroundImage:
            'linear-gradient(rgba(0,240,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,0.3) 1px, transparent 1px)',
          backgroundSize: '15px 15px',
        }}
      >
        <span className="absolute -top-3.5 right-1 text-[7px] text-hud-cyan font-mono font-bold">
          WET SURFACE SECTOR
        </span>
      </div>

      {/* 3. Center Vehicle Tracking Reticle with Cockpit Arc (from 2.jpg) */}
      <div
        className="tracking-box absolute transition-all duration-700 ease-out"
        style={{
          top: '36%',
          left: '38%',
          width: '24%',
          height: '28%',
          minWidth: '220px',
          minHeight: '150px',
        }}
        data-tag="CAR #42 [IDENTIFIED]"
      >
        {/* Cockpit HUD Arc Overlay */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-60" viewBox="0 0 200 150">
          <circle
            cx="100"
            cy="70"
            r="45"
            fill="none"
            stroke="#00f0ff"
            strokeWidth="1.5"
            strokeDasharray="40 20"
            className="animate-spin"
            style={{ transformOrigin: '100px 70px', animationDuration: '12s' }}
          />
          <circle cx="100" cy="70" r="30" fill="none" stroke="#00f0ff" strokeWidth="0.8" strokeDasharray="4 4" />
        </svg>

        {/* Distance measurement label at bottom of car */}
        <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 px-2 py-0.5 rounded bg-hud-bg/90 border border-hud-cyan text-[7.5px] font-bold text-hud-cyan shadow-[0_0_8px_rgba(0,240,255,0.4)]">
          12.6 m
        </div>

        {/* Corner Reticles */}
        <div className="absolute -top-1 -left-1 w-2.5 h-2.5 border-t-2 border-l-2 border-hud-cyan" />
        <div className="absolute -top-1 -right-1 w-2.5 h-2.5 border-t-2 border-r-2 border-hud-cyan" />
        <div className="absolute -bottom-1 -left-1 w-2.5 h-2.5 border-b-2 border-l-2 border-hud-cyan" />
        <div className="absolute -bottom-1 -right-1 w-2.5 h-2.5 border-b-2 border-r-2 border-hud-cyan" />
      </div>

      {/* 4. Trajectory / Dynamic Racing Line SVG */}
      <svg
        className="absolute inset-0 w-full h-full opacity-40"
        viewBox="0 0 1000 1000"
        preserveAspectRatio="none"
      >
        <path
          d="M360 960 Q 480 480 640 370 T 820 290"
          fill="none"
          stroke={isWet ? '#00f0ff' : isDamp ? '#ffb000' : '#00ff88'}
          strokeWidth="3.5"
          strokeDasharray="14,8"
          className="animate-pulse"
        />
      </svg>

      {/* 5. Surface Grip Callout */}
      <div
        className="absolute technical-border bg-hud-bg/85 backdrop-blur-md p-2.5 shadow-[0_0_15px_rgba(0,0,0,0.8)] border border-hud-cyan/30"
        style={{
          top: '52%',
          left: '64%',
        }}
      >
        <div className="flex items-center gap-1.5 mb-1">
          <span className="w-1.5 h-1.5 rounded-full bg-hud-cyan animate-pulse" />
          <p className="text-[7.5px] text-hud-dim tracking-wider font-bold">SURFACE: ASPHALT</p>
        </div>
        <p className="text-[8.5px] text-hud-cyan font-bold">
          GRIP: {gripLevel} [{isWet ? 'WET DEGRADED' : isDamp ? 'DAMP SLIP' : 'OPTIMAL'}]
        </p>
      </div>
    </div>
  );
};
