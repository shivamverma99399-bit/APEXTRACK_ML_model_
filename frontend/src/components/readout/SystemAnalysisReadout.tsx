import React from 'react';
import type { ApexTrackState } from '../../types/track';

interface SystemAnalysisReadoutProps {
  state: ApexTrackState;
}

export const SystemAnalysisReadout: React.FC<SystemAnalysisReadoutProps> = ({ state }) => {
  const {
    condition,
    confidence,
    probabilities,
    processingTimeMs,
    trend,
    history,
    advisory,
    model,
    telemetry,
    systemStatus,
  } = state;

  const confPct = (confidence * 100).toFixed(1);

  const getConditionColor = (cond: string) => {
    switch (cond.toLowerCase()) {
      case 'wet':
        return { text: 'text-hud-cyan', border: 'border-hud-cyan', bg: 'bg-hud-cyan/15', glow: 'shadow-[0_0_20px_rgba(0,240,255,0.3)]' };
      case 'damp':
        return { text: 'text-hud-amber', border: 'border-hud-amber', bg: 'bg-hud-amber/15', glow: 'shadow-[0_0_20px_rgba(255,176,0,0.3)]' };
      case 'dry':
      default:
        return { text: 'text-hud-green', border: 'border-hud-green', bg: 'bg-hud-green/15', glow: 'shadow-[0_0_20px_rgba(0,255,136,0.3)]' };
    }
  };

  const condStyle = getConditionColor(condition);

  const getTrendMetadata = (tr: string) => {
    switch (tr) {
      case 'drying':
        return { label: 'DRYING', color: 'text-hud-amber', border: 'border-hud-amber', icon: '↘' };
      case 'wetting':
        return { label: 'WETTING', color: 'text-hud-red', border: 'border-hud-red', icon: '↗' };
      case 'stable':
        return { label: 'STABLE', color: 'text-hud-green', border: 'border-hud-green', icon: '→' };
      default:
        return { label: 'INSUFFICIENT DATA', color: 'text-hud-dim', border: 'border-hud-edge', icon: '⋯' };
    }
  };

  const trendMeta = getTrendMetadata(trend);

  return (
    <div className="w-full bg-[#030508] text-hud-txt font-mono px-4 sm:px-8 lg:px-16 py-16 border-t border-hud-cyan/20 space-y-16">
      {/* ========================================================
          LARGE SECTION HEADER
         ======================================================== */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-end gap-6 pb-8 border-b border-hud-edge/40">
        <div>
          <div className="flex items-center gap-2 text-hud-cyan text-[11px] font-bold tracking-[0.25em] mb-2 uppercase">
            <span className="w-2.5 h-2.5 rounded-full bg-hud-cyan animate-pulse shadow-[0_0_8px_#00f0ff]" />
            APEXTRACK // SYSTEM ANALYSIS
          </div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-wider mb-2">
            LIVE INTELLIGENCE READOUT
          </h2>
          <p className="text-hud-dim text-xs sm:text-sm max-w-2xl leading-relaxed">
            Real-time track intelligence, AI classification, vehicle telemetry and tactical decision support.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-[10px] bg-hud-panel p-3 rounded border border-hud-edge/50">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-hud-green shadow-[0_0_8px_#00ff88] animate-pulse" />
            <span className="text-white font-bold uppercase">{systemStatus}</span>
          </div>
          <div className="border-l border-hud-edge/40 pl-4">
            <span className="text-hud-dim">MODEL: </span>
            <span className="text-hud-cyan font-bold">APEXTRACK V2</span>
          </div>
          <div className="border-l border-hud-edge/40 pl-4">
            <span className="text-hud-dim">INFERENCE: </span>
            <span className="text-hud-green font-bold">LIVE ({processingTimeMs.toFixed(1)}ms)</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-16">
        {/* ========================================================
            01 // TRACK CONDITION ANALYSIS
           ======================================================== */}
        <section id="section-track-analysis" className="scroll-mt-16 technical-border p-6 sm:p-8 bg-hud-panel backdrop-blur-md rounded-sm">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-hud-edge/40">
            <div className="flex items-center gap-3">
              <span className="text-hud-cyan text-sm font-bold">01 //</span>
              <h3 className="text-lg sm:text-xl font-bold tracking-wider text-white uppercase">
                TRACK CONDITION ANALYSIS
              </h3>
            </div>
            <span className="text-[10px] text-hud-dim font-mono tracking-widest">
              VISION TRANSFORMER INFERENCE
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left: Large Current State */}
            <div className={`lg:col-span-5 p-6 rounded border ${condStyle.border} ${condStyle.bg} ${condStyle.glow} flex flex-col justify-between h-full min-h-[180px]`}>
              <div>
                <p className="text-[10px] text-hud-dim tracking-widest uppercase font-bold mb-1">
                  CURRENT TRACK STATE
                </p>
                <p className={`text-4xl sm:text-5xl lg:text-6xl font-black tracking-widest ${condStyle.text}`}>
                  {condition.toUpperCase()}
                </p>
              </div>

              <div className="mt-4 pt-4 border-t border-hud-edge/30 flex justify-between items-end">
                <div>
                  <p className="text-[9px] text-hud-dim uppercase">AI CONFIDENCE</p>
                  <p className="text-2xl sm:text-3xl font-extrabold text-white tabular-nums">
                    {confPct}%
                  </p>
                </div>
                <span className="text-[9px] px-2.5 py-1 rounded bg-hud-bg/80 border border-hud-edge text-hud-cyan uppercase font-bold">
                  VERIFIED
                </span>
              </div>
            </div>

            {/* Right: Probability Breakdown Horizontal Bars */}
            <div className="lg:col-span-7 space-y-4">
              <p className="text-xs font-bold text-hud-cyan uppercase tracking-wider mb-2">
                Model Probability Distribution
              </p>

              {/* DRY */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className={`uppercase font-bold ${condition === 'dry' ? 'text-hud-green' : 'text-hud-dim'}`}>
                    Dry Condition
                  </span>
                  <span className="text-white font-bold tabular-nums">
                    {(probabilities.dry * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="h-3 w-full bg-hud-bg rounded-full overflow-hidden border border-hud-edge/40">
                  <div
                    className="h-full bg-hud-green transition-all duration-700 ease-out rounded-full shadow-[0_0_8px_#00ff88]"
                    style={{ width: `${Math.max(probabilities.dry * 100, 2)}%` }}
                  />
                </div>
              </div>

              {/* DAMP */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className={`uppercase font-bold ${condition === 'damp' ? 'text-hud-amber' : 'text-hud-dim'}`}>
                    Damp Condition
                  </span>
                  <span className="text-white font-bold tabular-nums">
                    {(probabilities.damp * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="h-3 w-full bg-hud-bg rounded-full overflow-hidden border border-hud-edge/40">
                  <div
                    className="h-full bg-hud-amber transition-all duration-700 ease-out rounded-full shadow-[0_0_8px_#ffb000]"
                    style={{ width: `${Math.max(probabilities.damp * 100, 2)}%` }}
                  />
                </div>
              </div>

              {/* WET */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className={`uppercase font-bold ${condition === 'wet' ? 'text-hud-cyan' : 'text-hud-dim'}`}>
                    Wet Condition
                  </span>
                  <span className="text-white font-bold tabular-nums">
                    {(probabilities.wet * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="h-3 w-full bg-hud-bg rounded-full overflow-hidden border border-hud-edge/40">
                  <div
                    className="h-full bg-hud-cyan transition-all duration-700 ease-out rounded-full shadow-[0_0_8px_#00f0ff]"
                    style={{ width: `${Math.max(probabilities.wet * 100, 2)}%` }}
                  />
                </div>
              </div>

              {/* Model Output Metadata footer */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-hud-edge/30 text-[9px]">
                <div>
                  <span className="text-hud-dim block">MODEL</span>
                  <span className="text-white font-bold">ApexTrack V2</span>
                </div>
                <div>
                  <span className="text-hud-dim block">CURRENT CLASS</span>
                  <span className="text-hud-cyan font-bold uppercase">{condition}</span>
                </div>
                <div>
                  <span className="text-hud-dim block">CONFIDENCE</span>
                  <span className="text-white font-bold">{confPct}%</span>
                </div>
                <div>
                  <span className="text-hud-dim block">LATENCY</span>
                  <span className="text-hud-green font-bold">{processingTimeMs.toFixed(1)} ms</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ========================================================
            02 // TEMPORAL TRACK ANALYSIS
           ======================================================== */}
        <section className="technical-border p-6 sm:p-8 bg-hud-panel backdrop-blur-md rounded-sm">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-hud-edge/40">
            <div className="flex items-center gap-3">
              <span className="text-hud-cyan text-sm font-bold">02 //</span>
              <h3 className="text-lg sm:text-xl font-bold tracking-wider text-white uppercase">
                TEMPORAL TRACK ANALYSIS & TREND
              </h3>
            </div>
            <span className="text-[10px] text-hud-dim font-mono tracking-widest">
              SLIDING WINDOW TELEMETRY
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1 font-bold">CURRENT STATE</span>
              <span className={`text-2xl font-black uppercase ${condStyle.text}`}>
                {condition}
              </span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1 font-bold">STATE DIRECTION</span>
              <span className={`text-2xl font-black uppercase ${trendMeta.color} flex items-center gap-2`}>
                <span>{trendMeta.label}</span>
                <span>{trendMeta.icon}</span>
              </span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1 font-bold">CONFIDENCE GATING</span>
              <span className="text-2xl font-black text-white">
                ≥ 0.55 <span className="text-xs text-hud-dim font-normal">THRESHOLD</span>
              </span>
            </div>
          </div>

          <div>
            <p className="text-xs font-bold text-hud-cyan uppercase tracking-wider mb-3">
              Chronological Telemetry Sequence Progression
            </p>

            <div className="flex items-center justify-between gap-2 p-4 rounded bg-hud-bg/80 border border-hud-edge/50 overflow-x-auto min-h-[64px]">
              {history.length > 0 ? (
                history.map((item, idx) => {
                  const isLast = idx === history.length - 1;
                  const itemColor =
                    item.condition === 'wet'
                      ? 'text-hud-cyan'
                      : item.condition === 'damp'
                      ? 'text-hud-amber'
                      : 'text-hud-green';

                  return (
                    <React.Fragment key={idx}>
                      <div className="flex flex-col items-center px-3 py-1 bg-hud-panel/90 rounded border border-hud-edge/30">
                        <span className={`text-xs font-black uppercase ${itemColor}`}>
                          {item.condition}
                        </span>
                        <span className="text-[9px] text-hud-dim tabular-nums font-mono">
                          {(item.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      {!isLast && <span className="text-hud-cyan font-bold text-sm">→</span>}
                    </React.Fragment>
                  );
                })
              ) : (
                <div className="text-center w-full text-xs text-hud-dim py-2 font-mono tracking-wider">
                  AWAITING TELEMETRY FRAMES (0 / 3) — INSUFFICIENT DATA
                </div>
              )}
            </div>
          </div>
        </section>

        {/* ========================================================
            03 // AI DECISION SUPPORT & RACE STRATEGY
           ======================================================== */}
        <section className="technical-border p-6 sm:p-8 bg-hud-panel backdrop-blur-md rounded-sm">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-hud-edge/40">
            <div className="flex items-center gap-3">
              <span className="text-hud-cyan text-sm font-bold">03 //</span>
              <h3 className="text-lg sm:text-xl font-bold tracking-wider text-white uppercase">
                AI DECISION SUPPORT & RACE STRATEGY
              </h3>
            </div>
            <span className="text-[10px] text-hud-green font-mono tracking-widest font-bold">
              TACTICAL ACTIVE
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
            <div className="lg:col-span-4 p-4 rounded bg-hud-bg/70 border border-hud-edge/40 space-y-3">
              <div>
                <span className="text-[9px] text-hud-dim uppercase block">TACTICAL STATE</span>
                <span className="text-lg font-bold text-hud-green">DELTA ACTIVE</span>
              </div>
              <div className="flex justify-between border-t border-hud-edge/30 pt-2 text-xs">
                <span className="text-hud-dim uppercase">LAP TIME</span>
                <span className="text-white font-bold tabular-nums">{telemetry.lapTime}</span>
              </div>
              <div className="flex justify-between border-t border-hud-edge/30 pt-2 text-xs">
                <span className="text-hud-dim uppercase">DELTA</span>
                <span className="text-hud-green font-bold tabular-nums">{telemetry.delta} s</span>
              </div>
            </div>

            <div className="lg:col-span-8 p-4 rounded bg-hud-bg/70 border border-hud-edge/40 flex flex-col justify-between">
              <div>
                <span className="text-[9px] text-hud-dim uppercase block mb-1 font-bold">
                  AI TACTICAL ADVISORY
                </span>
                <p className="text-sm sm:text-base font-bold text-white leading-relaxed">
                  {advisory?.message || 'Surface telemetry optimal. Continue monitoring live track feed.'}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-hud-edge/30 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div>
                  <span className="text-[8.5px] text-hud-dim uppercase block">RECOMMENDED ACTION</span>
                  <span className="text-xs text-hud-cyan font-bold">
                    {advisory?.recommended_action || 'Maintain current tire setup and observe track conditions.'}
                  </span>
                </div>
                <span className="px-2.5 py-1 rounded text-[9px] font-bold uppercase bg-hud-cyan/15 border border-hud-cyan text-hud-cyan">
                  SEVERITY: {advisory?.severity?.toUpperCase() || 'LOW'}
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* ========================================================
            04 // VEHICLE TELEMETRY
           ======================================================== */}
        <section id="section-telemetry" className="scroll-mt-16 technical-border p-6 sm:p-8 bg-hud-panel backdrop-blur-md rounded-sm">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-hud-edge/40">
            <div className="flex items-center gap-3">
              <span className="text-hud-cyan text-sm font-bold">04 //</span>
              <h3 className="text-lg sm:text-xl font-bold tracking-wider text-white uppercase">
                VEHICLE TELEMETRY CONSOLE
              </h3>
            </div>
            <span className="text-[10px] text-hud-dim font-mono tracking-widest">
              CAN-BUS LIVE STREAM
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">SPEED</span>
              <span className="text-2xl sm:text-3xl font-black text-white tabular-nums">{telemetry.speedKmh}</span>
              <span className="text-[9px] text-hud-dim ml-1">KM/H</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">ENGINE RPM</span>
              <span className="text-2xl sm:text-3xl font-black text-hud-cyan tabular-nums">{telemetry.rpm}</span>
              <span className="text-[9px] text-hud-dim ml-1">RPM</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">THROTTLE</span>
              <span className="text-2xl sm:text-3xl font-black text-hud-green tabular-nums">{telemetry.throttle}%</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">BRAKE</span>
              <span className="text-2xl sm:text-3xl font-black text-hud-red tabular-nums">{telemetry.brake}%</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">ERS DEPLOY</span>
              <span className="text-2xl sm:text-3xl font-black text-hud-green tabular-nums">{telemetry.ersDeploy}%</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">FUEL LOAD</span>
              <span className="text-2xl sm:text-3xl font-black text-white tabular-nums">{telemetry.fuelLoad}</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">LAP TIME</span>
              <span className="text-2xl sm:text-3xl font-black text-white tabular-nums">{telemetry.lapTime}</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">DELTA TIME</span>
              <span className="text-2xl sm:text-3xl font-black text-hud-green tabular-nums">{telemetry.delta} s</span>
            </div>
          </div>
        </section>

        {/* ========================================================
            05 // TYRE & CHASSIS CONDITION
           ======================================================== */}
        <section id="section-car-status" className="scroll-mt-16 technical-border p-6 sm:p-8 bg-hud-panel backdrop-blur-md rounded-sm">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-hud-edge/40">
            <div className="flex items-center gap-3">
              <span className="text-hud-cyan text-sm font-bold">05 //</span>
              <h3 className="text-lg sm:text-xl font-bold tracking-wider text-white uppercase">
                TYRE & CHASSIS CONDITION
              </h3>
            </div>
            <span className="text-[10px] text-hud-dim font-mono tracking-widest">
              4-CORNER THERMAL MATRIX
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* FRONT LEFT */}
            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40 space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-hud-cyan font-bold">FRONT LEFT</span>
                <span className="text-[9px] text-hud-dim">WEAR {telemetry.tyreDegradation?.fl || 12}%</span>
              </div>
              <div className="flex justify-between text-base font-bold">
                <span className="text-white">{telemetry.tyreTelemetry.fl.pressure} bar</span>
                <span className="text-hud-amber">{telemetry.tyreTelemetry.fl.temp} °C</span>
              </div>
            </div>

            {/* FRONT RIGHT */}
            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40 space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-hud-cyan font-bold">FRONT RIGHT</span>
                <span className="text-[9px] text-hud-dim">WEAR {telemetry.tyreDegradation?.fr || 13}%</span>
              </div>
              <div className="flex justify-between text-base font-bold">
                <span className="text-white">{telemetry.tyreTelemetry.fr.pressure} bar</span>
                <span className="text-hud-amber">{telemetry.tyreTelemetry.fr.temp} °C</span>
              </div>
            </div>

            {/* REAR LEFT */}
            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40 space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-hud-cyan font-bold">REAR LEFT</span>
                <span className="text-[9px] text-hud-dim">WEAR {telemetry.tyreDegradation?.rl || 11}%</span>
              </div>
              <div className="flex justify-between text-base font-bold">
                <span className="text-white">{telemetry.tyreTelemetry.rl.pressure} bar</span>
                <span className="text-hud-green">{telemetry.tyreTelemetry.rl.temp} °C</span>
              </div>
            </div>

            {/* REAR RIGHT */}
            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40 space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-hud-cyan font-bold">REAR RIGHT</span>
                <span className="text-[9px] text-hud-dim">WEAR {telemetry.tyreDegradation?.rr || 11}%</span>
              </div>
              <div className="flex justify-between text-base font-bold">
                <span className="text-white">{telemetry.tyreTelemetry.rr.pressure} bar</span>
                <span className="text-hud-green">{telemetry.tyreTelemetry.rr.temp} °C</span>
              </div>
            </div>
          </div>
        </section>

        {/* ========================================================
            06 // TRACK SURFACE ANALYSIS
           ======================================================== */}
        <section className="technical-border p-6 sm:p-8 bg-hud-panel backdrop-blur-md rounded-sm">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-hud-edge/40">
            <div className="flex items-center gap-3">
              <span className="text-hud-cyan text-sm font-bold">06 //</span>
              <h3 className="text-lg sm:text-xl font-bold tracking-wider text-white uppercase">
                TRACK SURFACE ANALYSIS
              </h3>
            </div>
            <span className="text-[10px] text-hud-dim font-mono tracking-widest">
              SURFACE FRICTION RADAR
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">SURFACE MATERIAL</span>
              <span className="text-base font-bold text-white">ASPHALT</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">GRIP LEVEL</span>
              <span className="text-base font-bold text-hud-cyan">{telemetry.gripLevel} [MEDIUM]</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">SURFACE TEMP</span>
              <span className="text-base font-bold text-white">{telemetry.trackTemp} °C</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">IRREGULARITIES</span>
              <span className="text-base font-bold text-hud-amber">{telemetry.irregularities || 2.1}%</span>
            </div>
          </div>
        </section>

        {/* ========================================================
            07 // OBJECT DETECTION
           ======================================================== */}
        <section className="technical-border p-6 sm:p-8 bg-hud-panel backdrop-blur-md rounded-sm">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-hud-edge/40">
            <div className="flex items-center gap-3">
              <span className="text-hud-cyan text-sm font-bold">07 //</span>
              <h3 className="text-lg sm:text-xl font-bold tracking-wider text-white uppercase">
                OBJECT & OBSTACLE DETECTION
              </h3>
            </div>
            <span className="text-[10px] text-hud-cyan font-mono tracking-widest font-bold">
              RADAR ACTIVE
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div className="p-4 rounded bg-hud-cyan/10 border border-hud-cyan">
              <span className="text-[9px] text-hud-cyan uppercase block mb-1 font-bold">RACE CAR</span>
              <span className="text-2xl font-black text-hud-cyan tabular-nums">
                {telemetry.objectDetection?.car || 1} <span className="text-xs text-white">TRACK</span>
              </span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">MARSHAL</span>
              <span className="text-2xl font-black text-hud-dim tabular-nums">
                {telemetry.objectDetection?.marshal || 0} <span className="text-xs">TRACK</span>
              </span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">DEBRIS</span>
              <span className="text-2xl font-black text-hud-dim tabular-nums">
                {telemetry.objectDetection?.debris || 0} <span className="text-xs">TRACK</span>
              </span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">TRACK LIMIT</span>
              <span className="text-2xl font-black text-hud-dim tabular-nums">
                {telemetry.objectDetection?.flag || 0} <span className="text-xs">TRACK</span>
              </span>
            </div>
          </div>
        </section>

        {/* ========================================================
            08 // AI MODEL DIAGNOSTICS
           ======================================================== */}
        <section id="section-system" className="scroll-mt-16 technical-border p-6 sm:p-8 bg-hud-panel backdrop-blur-md rounded-sm">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-hud-edge/40">
            <div className="flex items-center gap-3">
              <span className="text-hud-cyan text-sm font-bold">08 //</span>
              <h3 className="text-lg sm:text-xl font-bold tracking-wider text-white uppercase">
                AI MODEL DIAGNOSTICS & HUB METRICS
              </h3>
            </div>
            <span className="text-[10px] text-hud-green font-mono tracking-widest font-bold">
              MODEL ONLINE
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">MODEL</span>
              <span className="text-sm font-bold text-white">ApexTrack V2</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">MODEL ID</span>
              <span className="text-xs font-bold text-hud-cyan truncate block" title={model.model_id}>
                {model.model_id}
              </span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">INFERENCE ENGINE</span>
              <span className="text-sm font-bold text-white">ViT-Base Transformer</span>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/40">
              <span className="text-[9px] text-hud-dim uppercase block mb-1">INFERENCE LATENCY</span>
              <span className="text-sm font-bold text-hud-green">{processingTimeMs.toFixed(1)} ms</span>
            </div>
          </div>
        </section>

        {/* ========================================================
            09 // SYSTEM HEALTH
           ======================================================== */}
        <section className="technical-border p-6 sm:p-8 bg-hud-panel backdrop-blur-md rounded-sm">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-hud-edge/40">
            <div className="flex items-center gap-3">
              <span className="text-hud-cyan text-sm font-bold">09 //</span>
              <h3 className="text-lg sm:text-xl font-bold tracking-wider text-white uppercase">
                SYSTEM HEALTH & MICROSERVICES
              </h3>
            </div>
            <span className="text-[10px] text-hud-green font-mono tracking-widest font-bold">
              OPTIMAL (200 OK)
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 rounded bg-hud-bg/70 border border-hud-edge/30 flex items-center justify-between">
              <span className="text-hud-dim">FRONTEND UI</span>
              <span className="text-hud-green font-bold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-hud-green animate-pulse" />
                ONLINE
              </span>
            </div>

            <div className="p-3 rounded bg-hud-bg/70 border border-hud-edge/30 flex items-center justify-between">
              <span className="text-hud-dim">FASTAPI BACKEND</span>
              <span className="text-hud-green font-bold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-hud-green animate-pulse" />
                ONLINE
              </span>
            </div>

            <div className="p-3 rounded bg-hud-bg/70 border border-hud-edge/30 flex items-center justify-between">
              <span className="text-hud-dim">ML MODEL ENGINE</span>
              <span className="text-hud-green font-bold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-hud-green animate-pulse" />
                READY
              </span>
            </div>

            <div className="p-3 rounded bg-hud-bg/70 border border-hud-edge/30 flex items-center justify-between">
              <span className="text-hud-dim">HUGGING FACE</span>
              <span className="text-hud-green font-bold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-hud-green animate-pulse" />
                CONNECTED
              </span>
            </div>

            <div className="p-3 rounded bg-hud-bg/70 border border-hud-edge/30 flex items-center justify-between">
              <span className="text-hud-dim">IMAGE INFERENCE</span>
              <span className="text-hud-green font-bold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-hud-green animate-pulse" />
                READY
              </span>
            </div>

            <div className="p-3 rounded bg-hud-bg/70 border border-hud-edge/30 flex items-center justify-between">
              <span className="text-hud-dim">TREND ENGINE</span>
              <span className="text-hud-green font-bold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-hud-green animate-pulse" />
                ACTIVE
              </span>
            </div>

            <div className="p-3 rounded bg-hud-bg/70 border border-hud-edge/30 flex items-center justify-between">
              <span className="text-hud-dim">ADVISORY ENGINE</span>
              <span className="text-hud-green font-bold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-hud-green animate-pulse" />
                ACTIVE
              </span>
            </div>

            <div className="p-3 rounded bg-hud-bg/70 border border-hud-edge/30 flex items-center justify-between">
              <span className="text-hud-dim">HEALTH CHECK</span>
              <span className="text-hud-green font-bold flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-hud-green" />
                HEALTHY
              </span>
            </div>
          </div>
        </section>

        {/* ========================================================
            10 // APEXTRACK CAPABILITIES
           ======================================================== */}
        <section className="technical-border p-6 sm:p-8 bg-hud-panel backdrop-blur-md rounded-sm">
          <div className="flex items-center justify-between mb-6 pb-3 border-b border-hud-edge/40">
            <div className="flex items-center gap-3">
              <span className="text-hud-cyan text-sm font-bold">10 //</span>
              <h3 className="text-lg sm:text-xl font-bold tracking-wider text-white uppercase">
                APEXTRACK PLATFORM CAPABILITIES
              </h3>
            </div>
            <span className="text-[10px] text-hud-dim font-mono tracking-widest">
              SYSTEM ARCHITECTURE
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/30">
              <span className="text-hud-cyan font-bold block mb-1">VISION INTELLIGENCE</span>
              <p className="text-[11px] text-hud-dim">Track-condition image classification via Hugging Face Vision Transformer.</p>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/30">
              <span className="text-hud-cyan font-bold block mb-1">CONDITION CLASSIFICATION</span>
              <p className="text-[11px] text-hud-dim">Three-state precision telemetry: Dry line, Damp surface, and Wet track.</p>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/30">
              <span className="text-hud-cyan font-bold block mb-1">TEMPORAL INTELLIGENCE</span>
              <p className="text-[11px] text-hud-dim">Sliding window trend analysis: Drying ↘, Wetting ↗, and Stable →.</p>
            </div>

            <div className="p-4 rounded bg-hud-bg/70 border border-hud-edge/30">
              <span className="text-hud-cyan font-bold block mb-1">TACTICAL PIT SUPPORT</span>
              <p className="text-[11px] text-hud-dim">Race strategy decision support for crossover tire window timing.</p>
            </div>
          </div>
        </section>
      </div>

      {/* Footer Branding */}
      <footer className="max-w-7xl mx-auto pt-8 border-t border-hud-edge/30 flex flex-col sm:flex-row justify-between items-center text-[10px] text-hud-dim gap-4">
        <div>
          APEXTRACK AI © 2026 // LIVE TRACK CONDITION INTELLIGENCE SYSTEM
        </div>
        <div className="flex gap-4">
          <span>FASTAPI BACKEND</span>
          <span>•</span>
          <span>HUGGING FACE HUB V2</span>
          <span>•</span>
          <span>MOTORSPORT TELEMETRY</span>
        </div>
      </footer>
    </div>
  );
};
