"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Leaf, Sparkles, Stethoscope, Wand2 } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Field, Input, Textarea } from "@/components/ui/Field";
import { Spinner } from "@/components/ui/Spinner";
import { ImageDropzone } from "@/components/modules/ImageDropzone";
import { HealthResult } from "@/components/modules/HealthResult";
import { SpeciesResult } from "@/components/modules/SpeciesResult";
import { Citations } from "@/components/modules/Citations";
import { Markdown } from "@/components/modules/Markdown";
import { diagnose } from "@/lib/api";
import type { DiagnoseResponse, PlantConditions } from "@/lib/types";

const FIELDS: { key: keyof PlantConditions; label: string; unit: string; step?: number }[] = [
  { key: "temperature_c", label: "Temp", unit: "°C" },
  { key: "humidity_pct", label: "Humidity", unit: "%" },
  { key: "soil_moisture_pct", label: "Soil moist.", unit: "%" },
  { key: "light_hours", label: "Light", unit: "h" },
  { key: "soil_ph", label: "Soil pH", unit: "pH", step: 0.1 },
  { key: "watering_freq_per_week", label: "Water", unit: "/wk" },
  { key: "fertilizer_freq_per_month", label: "Fertilise", unit: "/mo" },
  { key: "plant_age_months", label: "Age", unit: "mo" },
];

const DEFAULTS: PlantConditions = {
  temperature_c: 23, humidity_pct: 45, soil_moisture_pct: 88, light_hours: 5,
  soil_ph: 6.4, watering_freq_per_week: 8, fertilizer_freq_per_month: 1, plant_age_months: 14,
};

const SERVICE_LABELS: Record<string, string> = {
  dl: "Vision",
  ml: "Health model",
  agent: "Assistant",
};

export default function DiagnosePage() {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState(
    "Why are the leaves yellowing and the soil staying soggy?",
  );
  const [values, setValues] = useState<PlantConditions>(DEFAULTS);
  const [useConditions, setUseConditions] = useState(true);
  const [result, setResult] = useState<DiagnoseResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (key: keyof PlantConditions, v: string) =>
    setValues((prev) => ({ ...prev, [key]: v === "" ? 0 : Number(v) }));

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await diagnose({
        file,
        question,
        conditions: useConditions ? values : undefined,
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Diagnosis failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container-flora py-14 md:py-20">
      <PageHeader
        eyebrow="The unified flow"
        title="Diagnose a plant"
        description="One request, three intelligences. Vision identifies the plant, the ML model scores its health, and the assistant fuses everything into a single grounded recommendation."
      />

      <form onSubmit={onSubmit} className="mt-12 grid gap-6 lg:grid-cols-[0.92fr_1.08fr]">
        {/* ── Inputs ──────────────────────────────────────────────── */}
        <div className="space-y-6">
          <Card className="p-7">
            <h2 className="mb-4 flex items-center gap-2 text-[1rem] font-semibold text-ink">
              <Leaf className="h-4 w-4 text-leaf" /> Photo
              <span className="ml-auto text-[0.74rem] font-normal text-muted">optional</span>
            </h2>
            <ImageDropzone file={file} onChange={setFile} />
          </Card>

          <Card className="p-7">
            <h2 className="mb-4 text-[1rem] font-semibold text-ink">Your question</h2>
            <Textarea
              rows={3}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Describe what you're seeing…"
            />
          </Card>

          <Card className="p-7">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-[1rem] font-semibold text-ink">Conditions</h2>
              <button
                type="button"
                onClick={() => setUseConditions((v) => !v)}
                className="focus-ring inline-flex items-center gap-2 text-[0.78rem] text-muted hover:text-forest"
              >
                <span
                  className={`relative h-4 w-7 rounded-full transition-colors ${
                    useConditions ? "bg-leaf" : "bg-line"
                  }`}
                >
                  <span
                    className={`absolute top-0.5 h-3 w-3 rounded-full bg-white transition-all ${
                      useConditions ? "left-3.5" : "left-0.5"
                    }`}
                  />
                </span>
                {useConditions ? "Included" : "Skipped"}
              </button>
            </div>
            <div
              className={`grid grid-cols-2 gap-3 transition-opacity sm:grid-cols-4 ${
                useConditions ? "" : "pointer-events-none opacity-40"
              }`}
            >
              {FIELDS.map((f) => (
                <Field key={f.key} label={f.label} unit={f.unit}>
                  <Input
                    type="number"
                    step={f.step ?? 1}
                    value={String(values[f.key])}
                    onChange={(e) => set(f.key, e.target.value)}
                  />
                </Field>
              ))}
            </div>
          </Card>

          <Button type="submit" size="lg" className="w-full" disabled={loading}>
            {loading ? (
              <>
                <Spinner className="h-4 w-4 text-ivory" /> Running diagnosis…
              </>
            ) : (
              <>
                <Stethoscope className="h-4 w-4" /> Run full diagnosis
              </>
            )}
          </Button>
          {error && <p className="text-[0.84rem] text-danger">{error}</p>}
        </div>

        {/* ── Results ─────────────────────────────────────────────── */}
        <div className="lg:sticky lg:top-24 lg:self-start">
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                className="space-y-6"
              >
                {/* Pipeline trace */}
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-[0.78rem] text-muted">Pipeline:</span>
                  {["dl", "ml", "agent"].map((s) => {
                    const used = result.services_called.includes(s);
                    return (
                      <Badge key={s} tone={used ? "leaf" : "neutral"} className={used ? "" : "opacity-50"}>
                        {used ? "✓" : "–"} {SERVICE_LABELS[s]}
                      </Badge>
                    );
                  })}
                </div>

                {result.species && (
                  <Card className="p-7">
                    <SpeciesResult data={result.species} />
                  </Card>
                )}
                {result.health && (
                  <Card className="p-7">
                    <HealthResult data={result.health} />
                  </Card>
                )}

                {/* Recommendation */}
                <Card className="overflow-hidden p-0">
                  <div className="flex items-center gap-2 border-b border-line bg-leaf/[0.04] px-6 py-4">
                    <Sparkles className="h-4 w-4 text-leaf" />
                    <h3 className="text-[1rem] font-semibold text-forest">Recommendation</h3>
                  </div>
                  <div className="space-y-4 p-6">
                    <Markdown content={result.advice} />
                    <Citations items={result.citations} />
                  </div>
                </Card>
              </motion.div>
            ) : (
              <motion.div key="empty" exit={{ opacity: 0 }}>
                <Card className="flex min-h-[28rem] flex-col items-center justify-center p-10 text-center">
                  <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-leaf/10 text-leaf">
                    <Stethoscope className="h-7 w-7" />
                  </span>
                  <p className="mt-5 text-[1.05rem] font-medium text-ink/85">
                    Your diagnosis will appear here
                  </p>
                  <p className="mt-2 max-w-sm text-[0.9rem] leading-relaxed text-muted">
                    Add a photo and conditions, then run the full pipeline. You'll
                    see the identified species, a health assessment with its
                    drivers, and one grounded recommendation with sources.
                  </p>
                  <div className="mt-8 flex flex-wrap justify-center gap-2">
                    {["Vision", "Health model", "Assistant"].map((s) => (
                      <Badge key={s} tone="neutral">
                        <Wand2 className="h-3 w-3" /> {s}
                      </Badge>
                    ))}
                  </div>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </form>
    </div>
  );
}
