import type {
  ClassProbabilities,
  HistoryItem,
  ModelMetadata,
  TireAdvisory,
  TrackCondition,
  TrendState,
} from '../types/track';

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface BackendHealthResponse {
  status: string;
  service: string;
  version: string;
  model?: {
    configured: boolean;
    provider: string;
    model_id: string;
  };
}

export interface BackendPredictionResult {
  condition: TrackCondition;
  confidence: number;
  probabilities: ClassProbabilities;
}

export interface BackendImageAnalysisResponse {
  analysis_id: string;
  timestamp: string;
  prediction: BackendPredictionResult;
  processing_time_ms: number;
  model: ModelMetadata;
  trend: TrendState;
  advisory: TireAdvisory;
}

export interface BackendTrackTrendResponse {
  history: HistoryItem[];
  trend: TrendState;
  advisory: TireAdvisory;
}

export class ApiError extends Error {
  statusCode: number;
  code?: string;

  constructor(message: string, statusCode: number = 500, code?: string) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.code = code;
  }
}

/**
 * Checks FastAPI backend health and model configuration status.
 */
export async function checkHealth(): Promise<BackendHealthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData?.error?.message || `Health check failed with status ${response.status}`,
        response.status,
        errorData?.error?.code
      );
    }

    return await response.json();
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(
      'Unable to connect to ApexTrack AI API service.',
      0,
      'NETWORK_ERROR'
    );
  }
}

/**
 * Uploads a track condition image to the backend for real ViT vision inference.
 */
export async function analyzeImage(file: File): Promise<BackendImageAnalysisResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/image`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message =
        errorData?.error?.message ||
        (response.status === 413
          ? 'Image file size exceeds limit (10MB).'
          : response.status === 415
          ? 'Unsupported image format. Please upload JPG, PNG, or WEBP.'
          : response.status === 503
          ? 'Vision model is not loaded on backend.'
          : `Analysis failed with HTTP ${response.status}`);

      throw new ApiError(message, response.status, errorData?.error?.code);
    }

    return await response.json();
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(
      'Network error while transmitting track image.',
      0,
      'NETWORK_ERROR'
    );
  }
}

/**
 * Fetches recent reliable telemetry history, calculated trend, and tactical tire advisory.
 */
export async function getTrackTrend(): Promise<BackendTrackTrendResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/track/trend`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData?.error?.message || `Trend query failed with status ${response.status}`,
        response.status,
        errorData?.error?.code
      );
    }

    return await response.json();
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(
      'Unable to retrieve track trend telemetry.',
      0,
      'NETWORK_ERROR'
    );
  }
}
