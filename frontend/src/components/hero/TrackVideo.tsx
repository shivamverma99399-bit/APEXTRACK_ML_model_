import React, { useRef, useEffect } from 'react';

interface TrackVideoProps {
  videoSrc?: string;
  cameraName?: string;
  circuitName?: string;
}

export const TrackVideo: React.FC<TrackVideoProps> = ({
  videoSrc = '/assets/videos/apextrack-track.mp4',
  cameraName = 'CAM 01 [FRONT - EAU ROUGE]',
  circuitName = 'SPA-FRANCORCHAMPS',
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play().catch((err) => {
        console.warn('Autoplay prevented or pending interaction:', err);
      });
    }
  }, []);

  return (
    <div className="hud-video-container">
      {/* Background Video */}
      <video
        ref={videoRef}
        autoPlay
        muted
        loop
        playsInline
        className="hud-video"
      >
        <source src={videoSrc} type="video/mp4" />
        <source src="/apextrack-track.mp4" type="video/mp4" />
      </video>

      {/* Cinematic Darkening & Vignette Overlays */}
      <div className="video-vignette" />
      <div className="video-horizontal-gradient" />
      <div className="video-vertical-gradient" />

      {/* Subtle In-Video Technical Camera Corner Markers */}
      <div className="absolute top-16 left-80 text-[8px] text-hud-dim tracking-widest pointer-events-none opacity-60 z-10 flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-hud-cyan animate-pulse" />
        <span>{cameraName}</span>
        <span className="text-hud-cyan">● LIVE FEED</span>
      </div>

      <div className="absolute top-16 right-80 text-[8px] text-hud-dim tracking-widest pointer-events-none opacity-60 z-10 text-right">
        <span>CIRCUIT: {circuitName}</span>
        <span className="ml-2 text-hud-amber">FPS: 60.0</span>
      </div>
    </div>
  );
};
