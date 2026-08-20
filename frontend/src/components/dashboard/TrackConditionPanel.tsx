import React, { useRef, useState } from 'react';
import type { ClassProbabilities, TrackCondition } from '../../types/track';

interface TrackConditionPanelProps {
  condition: TrackCondition;
  confidence: number;
  probabilities: ClassProbabilities;
  processingTimeMs?: number;
  isAnalyzing: boolean;
  onAnalyzeFile: (file: File) => void;
  errorMessage?: string | null;
  statusMessage?: string | null;
}

export const TrackConditionPanel: React.FC<TrackConditionPanelProps> = ({
  condition,
  confidence,
  probabilities,
  processingTimeMs = 412.8,
  isAnalyzing,
  onAnalyzeFile,
  errorMessage,
  statusMessage,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);

  const getBadgeStyle = (cond: TrackCondition) => {
    switch (cond) {
      case 'wet':
        return {
          border: 'border-hud-cyan',
          bg: 'bg-hud-cyan/15',
          text: 'text-hud-cyan',
          shadow: 'shadow-[0_0_24px_rgba(0,240,255,0.35)]',
          label: 'WET TRACK',
        };
      case 'damp':
        return {
          border: 'border-hud-amber',
          bg: 'bg-hud-amber/15',
          text: 'text-hud-amber',
          shadow: 'shadow-[0_0_24px_rgba(255,176,0,0.35)]',
          label: 'DAMP SURFACE',
        };
      case 'dry':
      default:
        return {
          border: 'border-hud-green',
          bg: 'bg-hud-green/15',
          text: 'text-hud-green',
          shadow: 'shadow-[0_0_24px_rgba(0,255,136,0.35)]',
          label: 'DRY LINE',
        };
    }
  };

  const badge = getBadgeStyle(condition);
  const confPct = (confidence * 100).toFixed(1);

  const handleFile = (file: File) => {
    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    onAnalyzeFile(file);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleSampleSelect = async (sampleName: string, fileName: string) => {
    try {
      const response = await fetch(`/assets/demo/${sampleName}`);
      const blob = await response.blob();
      const file = new File([blob], fileName, { type: 'image/jpeg' });
      handleFile(file);
    } catch {
      // Fallback
    }
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedFile(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="technical-border p-3.5 bg-hud-panel backdrop-blur-md rounded-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-2.5 border-b border-hud-edge/40 pb-2">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-hud-cyan animate-pulse" />
          <h3 className="data-label text-hud-cyan">Track Condition</h3>
        </div>
        <span className="text-[8px] text-hud-dim tracking-wider font-mono">
          INFERENCE: {processingTimeMs.toFixed(1)}ms
        </span>
      </div>

      {/* Main Condition Display */}
      <div
        className={`flex items-center justify-between p-3 rounded border ${badge.border} ${badge.bg} ${badge.shadow} mb-3 transition-all duration-500`}
      >
        <div>
          <p className="text-[8px] text-hud-dim tracking-widest uppercase font-bold">STATE CLASSIFICATION</p>
          <p className={`text-2xl lg:text-3xl font-extrabold tracking-wider ${badge.text}`}>
            {condition.toUpperCase()}
          </p>
        </div>
        <div className="text-right">
          <p className="text-[8px] text-hud-dim tracking-widest uppercase font-bold">CONFIDENCE</p>
          <p className="text-xl lg:text-2xl font-bold text-white tabular-nums">
            {confPct}%
          </p>
        </div>
      </div>

      {/* Model Probabilities Breakdown */}
      <div className="mb-3">
        <p className="data-label !text-[8px] mb-2 flex items-center justify-between">
          <span>Model Probabilities</span>
          <span className="text-hud-dim">ViT-Base V2</span>
        </p>

        <div className="space-y-2">
          {/* DRY */}
          <div>
            <div className="flex justify-between text-[8.5px] mb-0.5 font-mono">
              <span className={`uppercase ${condition === 'dry' ? 'text-hud-green font-bold' : 'text-hud-dim'}`}>
                Dry
              </span>
              <span className="text-white font-bold tabular-nums">
                {(probabilities.dry * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-1.5 w-full bg-hud-edge/20 rounded-full overflow-hidden">
              <div
                className="h-full bg-hud-green transition-all duration-700 ease-out rounded-full"
                style={{ width: `${Math.max(probabilities.dry * 100, 2)}%` }}
              />
            </div>
          </div>

          {/* DAMP */}
          <div>
            <div className="flex justify-between text-[8.5px] mb-0.5 font-mono">
              <span className={`uppercase ${condition === 'damp' ? 'text-hud-amber font-bold' : 'text-hud-dim'}`}>
                Damp
              </span>
              <span className="text-white font-bold tabular-nums">
                {(probabilities.damp * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-1.5 w-full bg-hud-edge/20 rounded-full overflow-hidden">
              <div
                className="h-full bg-hud-amber transition-all duration-700 ease-out rounded-full"
                style={{ width: `${Math.max(probabilities.damp * 100, 2)}%` }}
              />
            </div>
          </div>

          {/* WET */}
          <div>
            <div className="flex justify-between text-[8.5px] mb-0.5 font-mono">
              <span className={`uppercase ${condition === 'wet' ? 'text-hud-cyan font-bold' : 'text-hud-dim'}`}>
                Wet
              </span>
              <span className="text-white font-bold tabular-nums">
                {(probabilities.wet * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-1.5 w-full bg-hud-edge/20 rounded-full overflow-hidden">
              <div
                className="h-full bg-hud-cyan transition-all duration-700 ease-out rounded-full shadow-[0_0_6px_#00f0ff]"
                style={{ width: `${Math.max(probabilities.wet * 100, 2)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Real Image Feed Upload, Drag & Drop, and Fast Demo Triggers */}
      <div className="pt-2.5 border-t border-hud-edge/40">
        <div className="flex items-center justify-between mb-1.5">
          <span className="data-label !text-[7.5px] text-hud-cyan">AI Telemetry Input</span>
          {previewUrl && (
            <div className="flex items-center gap-1.5">
              <span className="text-[7.5px] text-hud-dim font-mono truncate max-w-[110px]">
                {selectedFile?.name || 'telemetry_scan.jpg'}
              </span>
              <button
                type="button"
                onClick={handleClear}
                className="text-[9px] text-hud-dim hover:text-hud-red font-bold px-1"
                title="Clear selected frame"
              >
                ✕
              </button>
            </div>
          )}
        </div>

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={handleFileChange}
        />

        {/* Interactive Drag & Drop Area */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragOver(true);
          }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => !isAnalyzing && fileInputRef.current?.click()}
          className={`p-2.5 rounded border border-dashed transition-all duration-300 text-center cursor-pointer flex flex-col items-center justify-center gap-1 ${
            isDragOver
              ? 'border-hud-cyan bg-hud-cyan/15 scale-[1.01]'
              : isAnalyzing
              ? 'border-hud-cyan/50 bg-hud-cyan/10 cursor-wait'
              : 'border-hud-edge/60 hover:border-hud-cyan hover:bg-hud-cyan/5 bg-hud-bg/60'
          }`}
        >
          {isAnalyzing ? (
            <div className="py-1 flex flex-col items-center gap-1.5 w-full">
              <div className="flex items-center gap-2 text-hud-cyan text-[8.5px] font-bold tracking-wider uppercase">
                <span className="w-2 h-2 rounded-full bg-hud-cyan animate-ping" />
                <span>AI INFERENCE PROCESSING...</span>
              </div>
              <div className="h-1 w-full bg-hud-edge/20 rounded-full overflow-hidden">
                <div className="h-full bg-hud-cyan w-3/4 animate-pulse rounded-full" />
              </div>
              <span className="text-[7px] text-hud-dim font-mono">MODEL: APEXTRACK V2</span>
            </div>
          ) : previewUrl ? (
            <div className="flex items-center justify-between w-full gap-2">
              <img
                src={previewUrl}
                alt="Track preview"
                className="w-9 h-7 object-cover rounded border border-hud-edge/40"
              />
              <div className="text-left flex-1">
                <p className="text-[8px] text-white font-bold uppercase">FRAME LOADED</p>
                <p className="text-[7px] text-hud-dim">Click to replace or re-analyze</p>
              </div>
              <span className="px-2 py-1 rounded text-[7.5px] font-bold bg-hud-cyan/20 border border-hud-cyan text-hud-cyan uppercase">
                RE-SCAN
              </span>
            </div>
          ) : (
            <>
              <div className="flex items-center gap-1.5 text-hud-cyan text-[8.5px] font-bold tracking-wider uppercase">
                <svg className="w-3 h-3 text-hud-cyan" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" />
                </svg>
                <span>UPLOAD TRACK FRAME</span>
              </div>
              <p className="text-[7px] text-hud-dim">Drop image here or click to browse</p>
            </>
          )}
        </div>

        {/* Quick Sample Selector for Live Hackathon Demos */}
        <div className="flex items-center justify-between gap-1.5 mt-2">
          <span className="text-[7px] text-hud-dim tracking-wider uppercase">TEST FEED:</span>
          <button
            type="button"
            disabled={isAnalyzing}
            onClick={() => handleSampleSelect('dry_sample.jpg', 'dry_0041.jpg')}
            className="px-2 py-0.5 rounded text-[7.5px] font-mono font-bold bg-hud-bg/70 hover:bg-hud-green/20 border border-hud-edge/50 hover:border-hud-green text-hud-green transition-all"
            title="Load Real Dry Track Image"
          >
            DRY
          </button>
          <button
            type="button"
            disabled={isAnalyzing}
            onClick={() => handleSampleSelect('damp_sample.jpg', 'damp_0006.jpg')}
            className="px-2 py-0.5 rounded text-[7.5px] font-mono font-bold bg-hud-bg/70 hover:bg-hud-amber/20 border border-hud-edge/50 hover:border-hud-amber text-hud-amber transition-all"
            title="Load Real Damp Track Image"
          >
            DAMP
          </button>
          <button
            type="button"
            disabled={isAnalyzing}
            onClick={() => handleSampleSelect('wet_sample.jpg', 'wet_0177.jpg')}
            className="px-2 py-0.5 rounded text-[7.5px] font-mono font-bold bg-hud-bg/70 hover:bg-hud-cyan/20 border border-hud-edge/50 hover:border-hud-cyan text-hud-cyan transition-all"
            title="Load Real Wet Track Image"
          >
            WET
          </button>
        </div>

        {/* Status / Error feedback */}
        {errorMessage && (
          <div className="mt-2 p-1.5 rounded bg-hud-red/15 border border-hud-red text-hud-red text-[8px] font-mono">
            {errorMessage}
          </div>
        )}
        {statusMessage && !errorMessage && (
          <div className="mt-2 p-1 rounded bg-hud-cyan/10 border border-hud-cyan/30 text-hud-cyan text-[7.5px] font-mono flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-hud-cyan" />
            <span>{statusMessage}</span>
          </div>
        )}
      </div>
    </div>
  );
};
