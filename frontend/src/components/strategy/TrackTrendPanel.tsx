import React from 'react';
import type { HistoryItem, TrendState } from '../../types/track';

interface TrackTrendPanelProps {
  trend: TrendState;
  history: HistoryItem[];
}

export const TrackTrendPanel: React.FC<TrackTrendPanelProps> = ({
  trend,
  history,
}) => {
  const getTrendMetadata = (tr: TrendState) => {
    switch (tr) {
      case 'drying':
        return {
          label: 'DRYING',
          color: 'text-hud-amber',
          border: 'border-hud-amber',
          bg: 'bg-hud-amber/15',
          description: 'Moisture evaporating. Track transitioning toward dry line.',
          icon: '↘',
        };
      case 'wetting':
        return {
          label: 'WETTING',
          color: 'text-hud-red',
          border: 'border-hud-red',
          bg: 'bg-hud-red/15',
          description: 'Precipitation increasing. Grip degradation imminent.',
          icon: '↗',
        };
      case 'stable':
        return {
          label: 'STABLE',
          color: 'text-hud-green',
          border: 'border-hud-green',
          bg: 'bg-hud-green/15',
          description: 'Surface conditions steady across sectors.',
          icon: '→',
        };
      default:
        return {
          label: 'INSUFFICIENT DATA',
          color: 'text-hud-dim',
          border: 'border-hud-edge',
          bg: 'bg-hud-bg/30',
          description: 'Aggregating reliable telemetry frames...',
          icon: '⋯',
        };
    }
  };

  const trendMeta = getTrendMetadata(trend);

  return (
    <div className="technical-border p-4 bg-hud-panel backdrop-blur-md rounded-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 border-b border-hud-edge/40 pb-2">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-hud-cyan animate-pulse" />
          <h3 className="data-label text-hud-cyan">Track Trend Engine</h3>
        </div>
        <span className="text-[8px] text-hud-dim font-mono">TEMPORAL ANALYSIS</span>
      </div>

      {/* Aggregate Trend State */}
      <div
        className={`flex items-center justify-between p-3 rounded border ${trendMeta.border} ${trendMeta.bg} mb-3 transition-all duration-500`}
      >
        <div>
          <p className="text-[8px] text-hud-dim tracking-widest uppercase font-bold">STATE DIRECTION</p>
          <p className={`text-xl lg:text-2xl font-black tracking-widest ${trendMeta.color} flex items-center gap-2`}>
            <span>{trendMeta.label}</span>
            <span className="text-2xl">{trendMeta.icon}</span>
          </p>
        </div>
        <div className="text-right">
          <span className="px-2 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider bg-hud-bg/80 text-hud-txt border border-hud-edge">
            {history.length >= 3 ? 'CALCULATED' : 'INITIALIZING'}
          </span>
        </div>
      </div>

      {/* Sequence Progression */}
      <div>
        <p className="data-label !text-[8px] mb-2 flex items-center justify-between">
          <span>Telemetry Progression</span>
          <span className="text-hud-dim font-normal">
            {history.length > 0 ? `${history.length} frames` : 'Awaiting input'}
          </span>
        </p>

        <div className="flex items-center justify-between gap-1 p-2 rounded bg-hud-bg/60 border border-hud-edge/30 min-h-[42px]">
          {history.length > 0 ? (
            history.map((item, idx) => {
              const isLast = idx === history.length - 1;
              const condColor =
                item.condition === 'wet'
                  ? 'text-hud-cyan'
                  : item.condition === 'damp'
                  ? 'text-hud-amber'
                  : 'text-hud-green';

              return (
                <React.Fragment key={idx}>
                  <div className="flex flex-col items-center">
                    <span className={`text-[9px] font-extrabold uppercase ${condColor}`}>
                      {item.condition}
                    </span>
                    <span className="text-[7.5px] text-hud-dim tabular-nums font-mono">
                      {(item.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  {!isLast && <span className="text-hud-dim text-[10px]">→</span>}
                </React.Fragment>
              );
            })
          ) : (
            <div className="text-center w-full text-[8.5px] text-hud-dim py-1 font-mono tracking-wider">
              AWAITING TELEMETRY FRAMES (0 / 3)
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
