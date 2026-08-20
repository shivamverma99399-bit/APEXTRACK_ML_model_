import React from 'react';
import type { TireAdvisory } from '../../types/track';

interface TireAdvisoryPanelProps {
  advisory: TireAdvisory;
}

export const TireAdvisoryPanel: React.FC<TireAdvisoryPanelProps> = ({ advisory }) => {
  const getSeverityStyle = (sev: string) => {
    switch (sev) {
      case 'high':
        return {
          border: 'border-hud-red',
          bg: 'bg-hud-red/15',
          badge: 'bg-hud-red text-black',
          text: 'text-hud-red',
          title: 'CRITICAL STRATEGY ALERT',
        };
      case 'medium':
        return {
          border: 'border-hud-amber',
          bg: 'bg-hud-amber/15',
          badge: 'bg-hud-amber text-black',
          text: 'text-hud-amber',
          title: 'TACTICAL WINDOW OPEN',
        };
      case 'low':
      default:
        return {
          border: 'border-hud-cyan',
          bg: 'bg-hud-cyan/15',
          badge: 'bg-hud-cyan text-black',
          text: 'text-hud-cyan',
          title: 'STANDARD MONITORING',
        };
    }
  };

  const style = getSeverityStyle(advisory.severity);

  return (
    <div className="technical-border p-4 bg-hud-panel backdrop-blur-md rounded-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 border-b border-hud-edge/40 pb-2">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-hud-amber animate-pulse" />
          <h3 className="data-label text-hud-amber">Race Strategy & Tyre Advisory</h3>
        </div>
        <span className={`px-2 py-0.5 rounded text-[8px] font-black uppercase ${style.badge}`}>
          {style.title}
        </span>
      </div>

      {/* Advisory Message */}
      <div className={`p-3 rounded border ${style.border} ${style.bg} mb-3`}>
        <p className="text-[8px] text-hud-dim tracking-wider uppercase font-bold mb-1">
          AI TACTICAL INSIGHT
        </p>
        <p className="text-xs lg:text-[13px] text-white font-bold leading-snug">
          {advisory.message}
        </p>
      </div>

      {/* Recommended Strategy Action */}
      <div className="bg-hud-bg/70 p-2.5 rounded border border-hud-edge/30">
        <p className="text-[7.5px] text-hud-cyan tracking-widest uppercase font-bold mb-1 flex items-center gap-1.5">
          <span>●</span> RECOMMENDED PIT DECISION
        </p>
        <p className="text-[10px] text-hud-txt leading-relaxed font-mono">
          {advisory.recommended_action}
        </p>
      </div>
    </div>
  );
};
