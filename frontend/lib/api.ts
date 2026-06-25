// Typed client for the FloraAI gateway.
// In the browser we call the Next.js rewrite at `/gw/*` (same-origin → no CORS).
// On the server we hit the gateway directly.

import type {
  AgentResponse,
  ChatMessage,
  DiagnoseResponse,
  HealthPrediction,
  PlantConditions,
  PlatformHealth,
  SpeciesPrediction,
} from "./types";

const BASE =
  typeof window === "undefined"
    ? process.env.GATEWAY_ORIGIN || "http://127.0.0.1:8000"
    : "/gw";

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function asJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new ApiError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

export async function getPlatformHealth(): Promise<PlatformHealth> {
  const res = await fetch(`${BASE}/health`, { cache: "no-store" });
  return asJson<PlatformHealth>(res);
}

export async function predictHealth(
  conditions: PlantConditions,
): Promise<HealthPrediction> {
  const res = await fetch(`${BASE}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(conditions),
  });
  return asJson<HealthPrediction>(res);
}

export async function identifySpecies(
  file: File,
): Promise<SpeciesPrediction> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/api/identify`, { method: "POST", body: form });
  return asJson<SpeciesPrediction>(res);
}

export async function chat(
  message: string,
  history: ChatMessage[] = [],
): Promise<AgentResponse> {
  const res = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });
  return asJson<AgentResponse>(res);
}

export async function diagnose(input: {
  file?: File | null;
  question: string;
  conditions?: Partial<PlantConditions>;
}): Promise<DiagnoseResponse> {
  const form = new FormData();
  if (input.file) form.append("file", input.file);
  form.append("question", input.question);
  if (input.conditions) {
    for (const [k, v] of Object.entries(input.conditions)) {
      if (v !== undefined && v !== null && !Number.isNaN(v)) {
        form.append(k, String(v));
      }
    }
  }
  const res = await fetch(`${BASE}/diagnose`, { method: "POST", body: form });
  return asJson<DiagnoseResponse>(res);
}
