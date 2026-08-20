import React, { useState, useEffect } from 'react';
import type { TelemetryData } from '../../types/track';

interface BottomTelemetryProps {
  telemetry: TelemetryData;
}

export const BottomTelemetry: React.FC<BottomTelemetryProps> = ({ telemetry }) => {
  const [currentRpm, setCurrentRpm] = useState<number>(telemetry.rpm);
  const [currentSpeed, setCurrentSpeed] = useState<number>(telemetry.speedKmh);
  const { fl, fr, rl, rr } = telemetry.tyreTelemetry;

  useEffect(() => {
    const interval = setInterval(() => {
      // Subtle realistic live jitter for telemetry feel
      setCurrentRpm(telemetry.rpm + Math.floor(Math.random() * 60) - 30);
      setCurrentSpeed(telemetry.speedKmh + Math.floor(Math.random() * 3) - 1);
    }, 120);

    return () => clearInterval(interval);
  }, [telemetry.rpm, telemetry.speedKmh]);

  const speedProgress = (currentSpeed / 350) * 283;

  return (
    <div className="absolute bottom-0 left-0 right-0 h-[140px] lg:h-[155px] z-40 flex items-center justify-between px-4 lg:px-6 bg-gradient-to-t from-hud-bg via-hud-bg/90 to-transparent pointer-events-none font-mono select-none">
      {/* 1. Left: 4-Corner Tire Telemetry & Chassis (from 2.jpg) */}
      <div className="flex items-center gap-3 bg-hud-panel/75 p-2 rounded border border-hud-edge/30 backdrop-blur-sm pointer-events-auto">
        <div className="text-[7.5px] space-y-1 text-right">
          <div className="text-hud-cyan font-bold">{fl.pressure} bar</div>
          <div className="text-white">{fl.temp} °C</div>
          <div className="text-hud-cyan font-bold pt-1">{rl.pressure} bar</div>
          <div className="text-white">{rl.temp} °C</div>
        </div>

        {/* Chassis Wireframe */}
        <div className="w-10 h-18 border border-hud-edge/40 relative rounded-sm flex flex-col justify-between p-1 bg-hud-bg/60">
          <div className="flex justify-between">
            <div className="w-2.5 h-4 bg-hud-cyan/30 border border-hud-cyan rounded-xs" />
            <div className="w-2.5 h-4 bg-hud-cyan/30 border border-hud-cyan rounded-xs" />
          </div>
          <div className="w-[1px] h-6 bg-hud-edge/40 mx-auto" />
          <div className="flex justify-between">
            <div className="w-2.5 h-4 bg-hud-cyan/30 border border-hud-cyan rounded-xs" />
            <div className="w-2.5 h-4 bg-hud-cyan/30 border border-hud-cyan rounded-xs" />
          </div>
        </div>

        <div className="text-[7.5px] space-y-1 text-left">
          <div className="text-hud-cyan font-bold">{fr.pressure} bar</div>
          <div className="text-white">{fr.temp} °C</div>
          <div className="text-hud-cyan font-bold pt-1">{rr.pressure} bar</div>
          <div className="text-white">{rr.temp} °C</div>
        </div>
      </div>

      {/* 2. Middle-Left: Throttle & Brake Pedals (from 2.jpg) */}
      <div className="hidden sm:flex flex-col gap-2 w-28 lg:w-36 bg-hud-panel/75 p-2 rounded border border-hud-edge/30 backdrop-blur-sm pointer-events-auto">
        <div className="space-y-0.5">
          <div className="flex justify-between text-[7.5px] uppercase">
            <span className="text-hud-dim">Throttle</span>
            <span className="text-white font-bold">{telemetry.throttle}%</span>
          </div>
          <div className="h-1.5 w-full bg-hud-edge/20 rounded-full overflow-hidden">
            <div className="h-full bg-hud-cyan rounded-full" style={{ width: `${telemetry.throttle}%` }} />
          </div>
        </div>

        <div className="space-y-0.5">
          <div className="flex justify-between text-[7.5px] uppercase">
            <span className="text-hud-dim">Brake</span>
            <span className="text-hud-red font-bold">{telemetry.brake}%</span>
          </div>
          <div className="h-1.5 w-full bg-hud-edge/20 rounded-full overflow-hidden">
            <div className="h-full bg-hud-red rounded-full shadow-[0_0_6px_#ff3344]" style={{ width: `${telemetry.brake}%` }} />
          </div>
        </div>
      </div>

      {/* 3. Center: Speedometer Gauge (from 2.jpg) */}
      <div className="flex flex-col items-center pointer-events-auto">
        <div className="gauge-container">
          <svg className="gauge-svg" width="115" height="115" viewBox="0 0 100 100">
            <circle className="gauge-bg" cx="50" cy="50" r="45" strokeWidth="5" />
            <circle
              className="gauge-fill"
              cx="50"
              cy="50"
              r="45"
              strokeWidth="5"
              style={{ strokeDashoffset: Math.max(283 - speedProgress, 20) }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center pt-1">
            <span className="text-3xl lg:text-4xl font-black text-white tabular-nums tracking-tighter">
              {currentSpeed}
            </span>
            <span className="text-[8px] text-hud-dim tracking-[0.25em]">KM/H</span>
          </div>
        </div>
      </div>

      {/* 4. Middle-Right: Engine RPM & ERS Deployment (from 2.jpg) */}
      <div className="hidden sm:flex flex-col gap-1.5 w-32 lg:w-44 bg-hud-panel/75 p-2 rounded border border-hud-edge/30 backdrop-blur-sm pointer-events-auto">
        <div>
          <div className="flex justify-between text-[7.5px] uppercase">
            <span className="text-hud-dim">Engine RPM</span>
            <span className="text-white font-bold tabular-nums">{currentRpm}</span>
          </div>
          <div className="h-1.5 w-full bg-hud-edge/20 rounded-full overflow-hidden mt-0.5">
            <div className="h-full bg-hud-cyan rounded-full" style={{ width: `${(currentRpm / 13000) * 100}%` }} />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-[7.5px] uppercase">
            <span className="text-hud-dim">ERS Deploy</span>
            <span className="text-hud-green font-bold">{telemetry.ersDeploy || 73}%</span>
          </div>
          <div className="h-1.5 w-full bg-hud-edge/20 rounded-full overflow-hidden mt-0.5">
            <div className="h-full bg-hud-green rounded-full shadow-[0_0_6px_#00ff88]" style={{ width: `${telemetry.ersDeploy || 73}%` }} />
          </div>
        </div>
      </div>

      {/* 5. Right: Circuit Sector 2 Map & Best Lap (from 2.jpg) */}
      <div className="hidden md:flex items-center gap-3 bg-hud-panel/75 p-2 rounded border border-hud-edge/30 backdrop-blur-sm pointer-events-auto">
        {/* Track Sector Silhouette */}
        <div className="w-18 h-14 relative flex items-center justify-center">
          <svg className="w-16 h-12" viewBox="0 0 100 60">
            <path
              d="M 10 40 L 40 40 Q 55 40 55 25 L 55 20 Q 55 10 70 10 L 85 10 Q 95 10 95 25 L 95 35 Q 95 50 80 50 L 30 50 Q 10 50 10 40 Z"
              fill="none"
              stroke="#8a95a8"
              strokeWidth="2"
            />
            {/* Active Sector Highlighting */}
            <path
              d="M 55 25 L 55 20 Q 55 10 70 10 L 85 10"
              fill="none"
              stroke="#00ff88"
              strokeWidth="3"
              className="animate-pulse"
            />
          </svg>
        </div>

        {/* Sector Telemetry */}
        <div className="text-[7.5px] space-y-0.5 text-right font-mono">
          <div className="text-hud-dim uppercase">SECTOR 2</div>
          <div className="text-sm font-bold text-white tracking-wider tabular-nums">
            {telemetry.sectorTelemetry?.time || '00:38.247'}
            <span className="text-[8px] text-hud-green font-normal ml-1">
              {telemetry.sectorTelemetry?.delta || '-0.124'}
            </span>
          </div>
          <div className="text-hud-dim pt-0.5">
            BEST LAP <span className="text-white font-bold">{telemetry.sectorTelemetry?.bestLap || '01:24.416'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
