// TypeScript mirrors of the backend Pydantic schemas
// (shared/flora_common/schemas.py). Kept in sync by hand — the contract is small.

export interface PlantConditions {
  temperature_c: number;
  humidity_pct: number;
  soil_moisture_pct: number;
  light_hours: number;
  soil_ph: number;
  watering_freq_per_week: number;
  fertilizer_freq_per_month: number;
  plant_age_months: number;
}

export type RiskLabel = "healthy" | "at_risk" | "diseased";

export interface HealthPrediction {
  risk_label: RiskLabel;
  risk_score: number;
  class_probabilities: Record<string, number>;
  top_drivers: Record<string, number>[];
  model_version: string;
}

export interface SpeciesPrediction {
  label: string;
  confidence: number;
  top_k: Record<string, number>[];
  model_version: string;
  low_confidence: boolean;
}

export interface Citation {
  source: string;
  snippet: string;
}

export interface AgentResponse {
  answer: string;
  citations: Citation[];
  tools_used: string[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface DiagnoseResponse {
  species: SpeciesPrediction | null;
  health: HealthPrediction | null;
  advice: string;
  citations: Citation[];
  services_called: string[];
}

export interface PlatformHealth {
  status: string;
  service: string;
  downstream: {
    ml: { status: string; model_loaded: boolean } | null;
    dl: { status: string; model_loaded: boolean } | null;
    agent: {
      status: string;
      vectorstore_ready: boolean;
      llm_enabled: boolean;
      model: string;
    } | null;
  };
}
