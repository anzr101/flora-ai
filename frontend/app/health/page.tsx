"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { LineChart, Wand2 } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field, Input } from "@/components/ui/Field";
import { Spinner } from "@/components/ui/Spinner";
import { HealthResult } from "@/components/modules/HealthResult";
import { predictHealth } from "@/lib/api";
import type { HealthPrediction, PlantConditions } from "@/lib/types";

const FIELDS: { key: keyof PlantConditions; label: string; unit: string; step?: number }[] = [
  { key: "temperature_c", label: "Temperature", unit: "°C" },
  { key: "humidity_pct", label: "Humidity", unit: "%" },
  { key: "soil_moisture_pct", label: "Soil moisture", unit: "%" },
  { key: "light_hours", label: "Daily light", unit: "hours" },
  { key: "soil_ph", label: "Soil pH", unit: "pH", step: 0.1 },
  { key: "watering_freq_per_week", label: "Watering", unit: "/ week" },
  { key: "fertilizer_freq_per_month", label: "Fertilising", unit: "/ month" },
  { key: "plant_age_months", label: "Plant age", unit: "months" },
];

const PRESETS: Record<string, PlantConditions> = {
  "Thriving": {
    temperature_c: 22, humidity_pct: 58, soil_moisture_pct: 48, light_hours: 10,
    soil_ph: 6.5, watering_freq_per_week: 3, fertilizer_freq_per_month: 2, plant_age_months: 24,
  },
  "Overwatered": {
    temperature_c: 21, humidity_pct: 70, soil_moisture_pct: 92, light_hours: 5,
    soil_ph: 6.3, watering_freq_per_week: 9, fertilizer_freq_per_month: 1, plant_age_months: 14,
  },
  "Heat-stressed": {
    temperature_c: 39, humidity_pct: 18, soil_moisture_pct: 8, light_hours: 14,
    soil_ph: 8.6, watering_freq_per_week: 0, fertilizer_freq_per_month: 0, plant_age_months: 5,
  },
};

export default function HealthPage() {
  const [values, setValues] = useState<PlantConditions>(PRESETS["Thriving"]);
  const [result, setResult] = useState<HealthPrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (key: keyof PlantConditions, v: string) =>
    setValues((prev) => ({ ...prev, [key]: v === "" ? 0 : Number(v) }));

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setResult(await predictHealth(values));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container-flora py-14 md:py-20">
      <PageHeader
        eyebrow="Module 01 · Classical ML"
        title="Plant health prediction"
        description="Estimate a plant's health-risk from its environment and care routine. The model returns calibrated probabilities and explains the factors behind each prediction."
      />

      <div className="mt-12 grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        {/* Input form */}
        <Card className="p-7">
          <div className="mb-5 flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-[1rem] font-semibold text-ink">
              <LineChart className="h-4 w-4 text-leaf" /> Conditions
            </h2>
            <div className="flex flex-wrap gap-1.5">
              {Object.keys(PRESETS).map((name) => (
                <button
                  key={name}
                  type="button"
                  onClick={() => setValues(PRESETS[name])}
                  className="focus-ring inline-flex items-center gap-1 rounded-full border border-line px-2.5 py-1 text-[0.74rem] text-muted transition-colors hover:border-leaf/50 hover:text-forest"
                >
                  <Wand2 className="h-3 w-3" /> {name}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={onSubmit}>
            <div className="grid gap-4 sm:grid-cols-2">
              {FIELDS.map((f) => (
                <Field key={f.key} label={f.label} unit={f.unit}>
                  <Input
                    type="number"
                    step={f.step ?? 1}
                    value={String(values[f.key])}
                    onChange={(e) => set(f.key, e.target.value)}
                    required
                  />
                </Field>
              ))}
            </div>
            <Button type="submit" size="lg" className="mt-6 w-full" disabled={loading}>
              {loading ? <Spinner className="h-4 w-4 text-ivory" /> : "Predict health"}
            </Button>
            {error && (
              <p className="mt-3 text-[0.84rem] text-danger">{error}</p>
            )}
          </form>
        </Card>

        {/* Result */}
        <Card className="p-7">
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              >
                <HealthResult data={result} />
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                exit={{ opacity: 0 }}
                className="flex h-full min-h-[20rem] flex-col items-center justify-center text-center"
              >
                <span className="flex h-14 w-14 items-center justify-center rounded-full bg-leaf/10 text-leaf">
                  <LineChart className="h-6 w-6" />
                </span>
                <p className="mt-4 text-[0.95rem] font-medium text-ink/80">No prediction yet</p>
                <p className="mt-1.5 max-w-xs text-[0.86rem] text-muted">
                  Adjust the conditions or pick a preset, then run the model to see
                  the risk breakdown and its drivers.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </Card>
      </div>
    </div>
  );
}
