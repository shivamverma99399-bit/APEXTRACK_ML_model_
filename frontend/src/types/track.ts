export type TrackCondition = 'dry' | 'damp' | 'wet';

export type TrendState = 'drying' | 'wetting' | 'stable' | 'insufficient_data';

export type HudNavTab = 'OVERVIEW' | 'TRACK ANALYSIS' | 'CAR STATUS' | 'TELEMETRY' | 'SYSTEM';

export interface ClassProbabilities {
  dry: number;
  damp: number;
  wet: number;
}

export interface TireAdvisory {
  severity: 'low' | 'medium' | 'high';
  message: string;
  recommended_action: string;
}

export interface HistoryItem {
  timestamp: string;
  condition: TrackCondition;
  confidence: number;
}

export interface ModelMetadata {
  provider: string;
  model_id: string;
  version?: string;
  configured?: boolean;
}

export interface ObjectDetectionData {
  car: number;
  marshal: number;
  debris: number;
  flag: number;
}

export interface TrackFeatureStatus {
  racingLine: { status: string; confidence: number };
  brakingZone: { distance: string; confidence: number };
  turnApex: { confidence: number };
  drsZone: { distance: string; confidence: number };
}

export interface TyreDegradation {
  fl: number;
  fr: number;
  rl: number;
  rr: number;
}

export interface TurnData {
  turnNumber: number;
  apexSpeed: number;
  entrySpeed: number;
  gear: number;
}

export interface SectorTelemetry {
  sectorNumber: number;
  time: string;
  delta: string;
  bestLap: string;
}

export interface TelemetryData {
  speedKmh: number;
  rpm: number;
  gear: number;
  throttle: number;
  brake: number;
  ersDeploy: number;
  ersHarvest: number;
  trackTemp: number;
  airTemp: number;
  humidity: number;
  windSpeed: number;
  windDirection: string;
  surfaceWearMm: number;
  irregularities: number;
  gripLevel: number;
  gripStatus: string;
  moistureLevel: number;
  currentLap: number;
  lapTime: string;
  bestLap: string;
  delta: string;
  fuelLoad: string;
  tyreDegradation: TyreDegradation;
  turnData: TurnData;
  sectorTelemetry: SectorTelemetry;
  trackFeatures: TrackFeatureStatus;
  objectDetection: ObjectDetectionData;
  tyreTelemetry: {
    fl: { pressure: number; temp: number };
    fr: { pressure: number; temp: number };
    rl: { pressure: number; temp: number };
    rr: { pressure: number; temp: number };
  };
}

export interface ApexTrackState {
  condition: TrackCondition;
  confidence: number;
  probabilities: ClassProbabilities;
  trend: TrendState;
  history: HistoryItem[];
  advisory: TireAdvisory;
  model: ModelMetadata;
  telemetry: TelemetryData;
  processingTimeMs: number;
  cameraName: string;
  circuitName: string;
  frameCount: number;
  systemStatus: 'ONLINE' | 'OPTIMAL' | 'DEGRADED' | 'OFFLINE';
  activeTab: HudNavTab;
}
