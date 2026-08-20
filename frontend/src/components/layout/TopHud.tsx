import React, { useState, useEffect } from 'react';
import type { HudNavTab, ModelMetadata, TrackCondition } from '../../types/track';

interface TopHudProps {
  model: ModelMetadata;
  condition: TrackCondition;
  cameraName?: string;
  frameCount?: number;
  systemStatus?: string;
  activeTab: HudNavTab;
  onTabChange: (tab: HudNavTab) => void;
  airTemp?: number;
}

const TABS: HudNavTab[] = ['OVERVIEW', 'TRACK ANALYSIS', 'CAR STATUS', 'TELEMETRY', 'SYSTEM'];

export const TopHud: React.FC<TopHudProps> = ({
  model,
  condition,
  cameraName = 'CAM 01 [FRONT]',
  frameCount = 1284,
  systemStatus = 'OPTIMAL',
  activeTab,
  onTabChange,
  airTemp = 23,
}) => {
  const [timeString, setTimeString] = useState<string>('12:46:38');
  const [liveFrames, setLiveFrames] = useState<number>(frameCount);

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      const pad = (n: number, z = 2) => String(n).padStart(z, '0');
      setTimeString(`${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`);
      setLiveFrames((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const getConditionBadge = (cond: TrackCondition) => {
    switch (cond) {
      case 'wet':
        return { text: 'TRACK WET', color: 'text-hud-cyan', border: 'border-hud-cyan/40', glow: 'shadow-[0_0_8px_rgba(0,240,255,0.4)]' };
      case 'damp':
        return { text: 'TRACK DAMP', color: 'text-hud-amber', border: 'border-hud-amber/40', glow: 'shadow-[0_0_8px_rgba(255,176,0,0.4)]' };
      case 'dry':
      default:
        return { text: 'TRACK DRY', color: 'text-hud-green', border: 'border-hud-green/40', glow: 'shadow-[0_0_8px_rgba(0,255,136,0.4)]' };
    }
  };

  const condBadge = getConditionBadge(condition);

  return (
    <header className="fixed top-0 left-0 w-full z-50 flex items-center justify-between px-4 lg:px-6 py-2 border-b border-hud-edge/40 bg-hud-bg/85 backdrop-blur-md font-mono select-none">
      {/* Left: Branding & Core Vision System */}
      <div className="flex items-center gap-4 lg:gap-8">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded border border-hud-cyan/40 bg-hud-cyan/10 flex items-center justify-center shadow-[0_0_8px_rgba(0,240,255,0.3)]">
            <svg className="w-3.5 h-3.5 text-hud-cyan" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3" />
              <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
            </svg>
          </div>
          <div>
            <h1 className="text-xs font-black tracking-[0.22em] text-white flex items-center gap-1.5">
              VISION <span className="text-hud-cyan">SYSTEM</span>
            </h1>
            <p className="text-[7px] text-hud-dim tracking-widest uppercase">
              APEXTRACK AI v2.0
            </p>
          </div>
        </div>

        {/* Live Camera Feed & Frame Count */}
        <div className="hidden xl:flex gap-4 items-center border-l border-hud-edge/40 pl-5 text-[8.5px]">
          <span className="text-hud-dim flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-hud-cyan animate-pulse" />
            {cameraName}
          </span>
          <span className="text-hud-dim">FRAME #{liveFrames}</span>
        </div>
      </div>

      {/* Center: Navigation Tabs from 2.jpg */}
      <nav className="hidden md:flex items-center gap-1 bg-hud-bg/60 p-1 rounded border border-hud-edge/30">
        {TABS.map((tab) => {
          const isActive = activeTab === tab;
          return (
            <button
              key={tab}
              type="button"
              onClick={() => onTabChange(tab)}
              className={`px-3 py-1 rounded text-[8.5px] font-bold tracking-wider uppercase transition-all duration-200 cursor-pointer ${
                isActive
                  ? 'bg-hud-cyan/20 border border-hud-cyan text-hud-cyan shadow-[0_0_10px_rgba(0,240,255,0.3)]'
                  : 'text-hud-dim hover:text-white hover:bg-hud-bg/80 border border-transparent'
              }`}
            >
              {tab}
            </button>
          );
        })}
      </nav>

      {/* Right: Time, Weather, and Real Track State */}
      <div className="flex items-center gap-4 lg:gap-6">
        {/* Clock */}
        <div className="flex items-center gap-1.5 text-hud-dim text-[9px]">
          <svg className="w-3 h-3 text-hud-dim" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          <span className="text-white font-bold tracking-wider tabular-nums">{timeString}</span>
        </div>

        {/* Ambient Temperature */}
        <div className="hidden sm:flex items-center gap-1 text-hud-dim text-[9px]">
          <svg className="w-3 h-3 text-hud-cyan" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z" />
          </svg>
          <span className="text-white font-bold">{airTemp}°C</span>
        </div>

        {/* Real Dynamic Track Condition Pill */}
        <div
          className={`flex items-center gap-1.5 px-2.5 py-0.5 rounded border ${condBadge.border} bg-hud-bg/80 ${condBadge.glow}`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-hud-cyan animate-ping" />
          <span className={`text-[8.5px] font-black uppercase tracking-wider ${condBadge.color}`}>
            {condBadge.text}
          </span>
        </div>

        {/* Model status indicator */}
        <div className="hidden lg:flex items-center gap-2 border-l border-hud-edge/40 pl-4">
          <div className="w-2 h-2 rounded-full bg-hud-green shadow-[0_0_6px_#00ff88] animate-pulse" />
          <span className="text-[8px] text-hud-dim uppercase font-bold" title={model.model_id}>
            {systemStatus}
          </span>
        </div>
      </div>
    </header>
  );
};
